#!/usr/bin/env python3
"""The Keel cockpit: a friendly, step-by-step control panel for building a product.

    python tools/keel.py           opens http://127.0.0.1:7799 in your browser

This is the easy face over everything Keel does. It never asks you to remember a
command. It shows you where you are on the journey, the single next thing to do
(in plain English, with the exact words to paste into your AI coding tool), and
lets you read everything Keel has written so far - the business case, the product
spec, the design, the plan - in the browser.

The complexity (the specialist agents, the rules, the quality gates) stays in the
back. This is the follow-along: open it, do the one step it shows you, come back,
refresh, do the next one. From an idea to a shipped product, without ever needing
to know what a "subagent" is.

Standard library only. Nothing to install.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import track  # the phase detector and the document register live here

ROOT = track.ROOT

# --------------------------------------------------------------------------- #
# The step, in plain English, for each phase. This is the whole point: the tool
# always knows the one next thing, and says it without jargon.
# --------------------------------------------------------------------------- #
STEPS: dict[str, dict[str, str]] = {
    "Pre-Discover": {
        "title": "Tell Keel your idea",
        "command": '/keel "your idea, in a sentence"',
        "why": "Everything starts from one clear idea. Say it in plain words.",
        "what": "Keel asks a couple of quick questions, then begins the research. "
                "You just answer and say go.",
    },
    "Discovering": {
        "title": "Research what exists, and how yours is better",
        "command": "/discover",
        "why": "Before building anything, Keel checks what already exists and makes "
               "sure your idea is genuinely better or newer - never a copy. (For a "
               "company, it also researches the market and the money.)",
        "what": "A specialist finds the existing products and projects and writes an "
                "honest verdict on how yours stands apart. Read it here when it's done.",
    },
    "Discover done": {
        "title": "Define the product",
        "command": "/define",
        "why": "Now Keel turns the idea into a precise plan for what the product "
               "actually does - every screen, every state.",
        "what": "A product manager writes the full specification, so nothing gets "
                "guessed later. This is what the build follows.",
    },
    "Define done": {
        "title": "Design how it looks and feels",
        "command": "/design",
        "why": "A distinctive design, not a generic template. You'll get real "
               "screen mockups you can open and look at.",
        "what": "A design lead creates the look, the colours and type, and mockups "
                "of the key screens. (If your idea has little UI, you can skip this "
                'by saying "skip to the technical plan".)',
    },
    "Design done": {
        "title": "Plan how it gets built",
        "command": "/architect",
        "why": "Keel chooses the technology and lays out the build in the right "
               "order, so nothing is built before the thing it needs.",
        "what": "An architect writes the technical plan and a step-by-step build "
                "roadmap, plus the list of accounts you'll need to set up.",
    },
    "Architect done": {
        "title": "Check it all holds together",
        "command": "/feasibility",
        "why": "The most important gate. Before a line of code, Keel audits the "
               "business, the product, and the build together.",
        "what": "An independent auditor gives a GO, REVISE, or NO-GO with reasons. "
                "If something's off, it tells you exactly what to fix.",
    },
    "Feasibility done": {
        "title": "Load the build plan",
        "command": "/plan",
        "why": "The plan passed. Now Keel turns the roadmap into a checklist of "
               "tasks it can build one at a time.",
        "what": "Every piece of the build becomes a tracked task in the right "
                "order. Then the building begins.",
    },
    "Building": {
        "title": "Build the next piece",
        "command": "/work",
        "why": "Keel decides what to build next, builds it properly, tests it, and "
               "proves it's secure - one piece at a time.",
        "what": 'Say "what\'s next?" (/next) to just see the recommendation, or '
                "/work to build it. Come back here to watch the progress fill in.",
    },
}

# The journey, in order, for the rail at the top.
JOURNEY = ["Idea", "Discover", "Define", "Design", "Architect", "Check", "Build", "Ship"]
PHASE_STAGE = {
    "Pre-Discover": 0, "Discovering": 1, "Discover done": 2, "Define done": 3,
    "Design done": 4, "Architect done": 5, "Feasibility done": 6, "Building": 6,
}


def state() -> dict:
    phase, nxt_cmd, why = track.detect_phase()
    step = STEPS.get(phase, STEPS["Building"])
    mode = track.detect_mode()
    docs = []
    for group, rel in track.register_for(mode):
        p = ROOT / rel
        docs.append({
            "group": group,
            "path": rel,
            "name": rel.split("/")[-1],
            "exists": p.exists(),
        })
    # build progress, if we're building
    tasks = track.load_all()
    done = sum(1 for t in tasks.values() if t.status == "done")
    return {
        "phase": phase,
        "mode": mode,
        "stage": PHASE_STAGE.get(phase, 0),
        "journey": JOURNEY,
        "step": step,
        "docs": docs,
        "build": {"done": done, "total": len(tasks)} if tasks else None,
    }


def read_doc(rel: str) -> dict:
    # Only allow reading inside spec/ and docs/, and never escape the repo.
    safe = (rel.startswith("spec/") or rel.startswith("docs/")) and ".." not in rel
    p = (ROOT / rel).resolve()
    if not safe or ROOT not in p.parents or not p.exists() or p.suffix.lower() != ".md":
        return {"error": "not found"}
    return {"path": rel, "html": md_to_html(p.read_text(encoding="utf-8"))}


# --------------------------------------------------------------------------- #
# A small, dependency-free Markdown -> HTML renderer. Enough to make the
# generated documents genuinely readable in the browser.
# --------------------------------------------------------------------------- #
def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"\[\[([^\]]+)\]\]", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', s)
        return s

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            block = []
            while i < n and not lines[i].startswith("```"):
                block.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(block) + "</code></pre>")
            continue
        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            out.append("<ul>")
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            out.append("<ol>")
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("</ol>")
            continue
        if line.lstrip().startswith(">"):
            out.append("<blockquote>")
            while i < n and lines[i].lstrip().startswith(">"):
                out.append(inline(re.sub(r"^\s*>\s?", "", lines[i])) + "<br>")
                i += 1
            out.append("</blockquote>")
            continue
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|?\s*$", lines[i + 1]):
            def cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip("|").split("|")]
            out.append("<table><thead><tr>")
            for c in cells(line):
                out.append(f"<th>{inline(c)}</th>")
            out.append("</tr></thead><tbody>")
            i += 2
            while i < n and lines[i].startswith("|"):
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(lines[i])) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue
        if re.match(r"^\s*---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        out.append("<p>" + inline(line) + "</p>")
        i += 1
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# HTTP.
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code: int, body, ctype="application/json"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, PAGE, "text/html")
        if self.path == "/api/state":
            return self._send(200, json.dumps(state()))
        if self.path.startswith("/api/doc?"):
            from urllib.parse import parse_qs, urlparse
            rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
            return self._send(200, json.dumps(read_doc(rel)))
        self._send(404, json.dumps({"error": "not found"}))


PAGE = r"""<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Keel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap">
<style>
:root{--bg:#f7f6f3;--panel:#fff;--ink:#1a1a17;--dim:#6b6a63;--line:#e7e5df;
--accent:#2f6f4f;--accent-soft:#2f6f4f14;--gold:#b0862b;--done:#2f6f4f}
@media(prefers-color-scheme:dark){:root{--bg:#14140f;--panel:#1c1c17;--ink:#ecebe4;
--dim:#9b9a90;--line:#2c2b24;--accent:#7fb89a;--accent-soft:#7fb89a1f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 Inter,system-ui,"Segoe UI",sans-serif}
.wrap{max-width:840px;margin:0 auto;padding:28px 22px 80px}
h1{font:600 26px/1.1 Fraunces,Georgia,serif;letter-spacing:-.01em;margin:0}
.sub{color:var(--dim);font-size:14px;margin-top:4px}
/* journey rail */
.rail{display:flex;gap:6px;align-items:center;margin:26px 0;flex-wrap:wrap}
.stop{display:flex;flex-direction:column;align-items:center;gap:5px;flex:1;min-width:64px}
.dot{width:26px;height:26px;border-radius:50%;background:var(--line);display:grid;
place-items:center;font-size:12px;color:var(--dim);font-weight:600}
.stop.done .dot{background:var(--done);color:#fff}
.stop.on .dot{background:var(--accent);color:#fff;box-shadow:0 0 0 4px var(--accent-soft)}
.stop small{font-size:11px;color:var(--dim)}
.stop.on small{color:var(--ink);font-weight:600}
/* next step card */
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;
padding:26px;box-shadow:0 1px 3px #0000000a}
.eyebrow{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);font-weight:600}
.card h2{font:600 22px/1.25 Fraunces,Georgia,serif;margin:8px 0 0}
.card .why{color:var(--ink);margin:12px 0 0}
.card .what{color:var(--dim);font-size:14.5px;margin:8px 0 0}
.cmd{display:flex;align-items:center;gap:10px;margin-top:20px;background:var(--accent-soft);
border:1px solid var(--accent);border-radius:11px;padding:12px 14px}
.cmd code{font:600 15px ui-monospace,Menlo,Consolas,monospace;color:var(--accent);flex:1}
.cmd button{border:0;background:var(--accent);color:#fff;font:600 13px Inter;padding:8px 14px;
border-radius:8px;cursor:pointer}
.hint{font-size:13px;color:var(--dim);margin-top:12px}
.hint b{color:var(--ink)}
/* produced docs */
h3{font:600 13px Inter;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);
margin:34px 0 12px}
.grp{margin-bottom:18px}
.grp .glabel{font-weight:600;font-size:14px;margin-bottom:8px}
.docs{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.doc{display:flex;align-items:center;gap:9px;padding:10px 12px;border:1px solid var(--line);
border-radius:10px;background:var(--panel);font-size:13.5px;cursor:pointer}
.doc.miss{opacity:.5;cursor:default}
.doc .tick{width:18px;height:18px;border-radius:50%;flex:none;display:grid;place-items:center;
font-size:11px;background:var(--line);color:var(--dim)}
.doc.have .tick{background:var(--done);color:#fff}
.doc:hover.have{border-color:var(--accent)}
/* reader */
#reader{position:fixed;inset:0 0 0 auto;width:min(760px,100%);background:var(--panel);
border-left:1px solid var(--line);transform:translateX(100%);transition:.18s;overflow:auto;
z-index:10;box-shadow:-20px 0 50px #00000018}
#reader.on{transform:none}
.rhead{position:sticky;top:0;background:var(--panel);border-bottom:1px solid var(--line);
padding:14px 22px;display:flex;justify-content:space-between;align-items:center}
.rhead b{font:600 14px ui-monospace,monospace}
.rhead button{border:0;background:var(--line);color:var(--ink);padding:6px 12px;border-radius:8px;cursor:pointer}
.rbody{padding:8px 30px 60px;font-size:15px}
.rbody h1{font-size:24px;margin:24px 0 8px}.rbody h2{font-size:19px;margin:22px 0 8px;font-family:Fraunces,serif}
.rbody h3{font-size:13px;text-transform:none;letter-spacing:0;color:var(--ink);margin:18px 0 6px}
.rbody table{width:100%;border-collapse:collapse;font-size:13.5px;margin:12px 0;display:block;overflow-x:auto}
.rbody th,.rbody td{border:1px solid var(--line);padding:7px 10px;text-align:left}
.rbody th{color:var(--dim);font-weight:600}
.rbody code{background:var(--accent-soft);padding:1px 5px;border-radius:4px;font-size:13px}
.rbody pre{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
.rbody blockquote{border-left:3px solid var(--accent);margin:12px 0;padding:2px 0 2px 16px;color:var(--dim)}
.rbody hr{border:0;border-top:1px solid var(--line);margin:20px 0}
#toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--ink);
color:var(--bg);padding:9px 16px;border-radius:9px;font-size:13px;opacity:0;transition:.2s;z-index:20}
#toast.on{opacity:1}
.foot{text-align:center;color:var(--dim);font-size:12.5px;margin-top:40px}
</style>

<div class=wrap>
  <h1>Keel</h1>
  <div class=sub>From your idea to a product you can ship. Here is your next step.</div>
  <div class=rail id=rail></div>
  <div class=card id=step></div>
  <div id=produced></div>
  <div class=foot>Do the step above in your AI coding tool, then come back and refresh.
    Keel keeps the hard parts in the back so you don't have to think about them.</div>
</div>
<div id=reader><div class=rhead><b id=rpath></b><button onclick="closeReader()">close</button></div>
  <div class=rbody id=rbody></div></div>
<div id=toast></div>

<script>
const $=s=>document.querySelector(s);
function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('on');
  clearTimeout(t._);t._=setTimeout(()=>t.classList.remove('on'),2200);}

async function load(){
  const s=await (await fetch('/api/state')).json();
  // rail
  $('#rail').innerHTML=s.journey.map((name,i)=>{
    const cls=i<s.stage?'done':(i===s.stage?'on':'');
    const mark=i<s.stage?'✓':(i+1);
    return `<div class="stop ${cls}"><div class=dot>${mark}</div><small>${name}</small></div>`;
  }).join('');
  // next step card
  const st=s.step;
  $('#step').innerHTML=`<div class=eyebrow>Your next step</div>
    <h2>${st.title}</h2>
    <div class=why>${st.why}</div>
    <div class=what>${st.what}</div>
    <div class=cmd><code>${st.command.replace(/</g,'&lt;')}</code>
      <button onclick="copyCmd(${JSON.stringify(st.command)})">Copy</button></div>
    <div class=hint>Paste that into <b>Claude Code</b> (or your AI coding tool),
      open in this project's folder, and press enter. ${s.build?`So far: <b>${s.build.done} of ${s.build.total}</b> build tasks done.`:''}</div>`;
  // produced docs, grouped
  const groups={};
  s.docs.forEach(d=>{(groups[d.group]=groups[d.group]||[]).push(d)});
  let h='<h3>What Keel has written so far</h3>';
  for(const g of ['Discover','Define','Design','Architect']){
    if(!groups[g])continue;
    h+=`<div class=grp><div class=glabel>${g}</div><div class=docs>`+
      groups[g].map(d=>`<div class="doc ${d.exists?'have':'miss'}" ${d.exists?`onclick="openDoc('${d.path}')"`:''}>
        <span class=tick>${d.exists?'✓':''}</span>${d.name.replace('.md','')}</div>`).join('')+
      `</div></div>`;
  }
  $('#produced').innerHTML=h;
}
function copyCmd(c){navigator.clipboard&&navigator.clipboard.writeText(c);toast('Copied. Paste it into your AI tool.');}
async function openDoc(path){
  const d=await (await fetch('/api/doc?path='+encodeURIComponent(path))).json();
  if(d.error){toast('Could not open that');return;}
  $('#rpath').textContent=path;$('#rbody').innerHTML=d.html;$('#reader').classList.add('on');
}
function closeReader(){$('#reader').classList.remove('on');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeReader()});
load();setInterval(load,4000);
</script>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=7799)
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()
    url = f"http://127.0.0.1:{a.port}/"
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"Keel cockpit  {url}")
    print("Your step-by-step guide from idea to shipped. Ctrl-C to stop.")
    if not a.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
