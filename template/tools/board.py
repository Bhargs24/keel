#!/usr/bin/env python3
"""The board: a local web UI over the same task files the CLI uses.

    make board          or      python tools/board.py [--port 7777] [--no-open]

Runs on localhost only, on the Python standard library, with no dependencies
and no database. It reads and writes tracker/tasks/*.md, so the CLI, git
history and CI checks all keep working: this is a different door onto the same
room, not a second source of truth.

Each person runs their own instance against their own working copy. Changes
are commits, and git merges them like anything else.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import track  # the model, the transitions and the rules all live there


# ------------------------------------------------------------------- payload

def snapshot() -> dict:
    tasks = track.load_all()
    people = track.load_people()
    out = []
    for t in sorted(tasks.values(), key=lambda x: (x.milestone, x.area, x.id)):
        blockers = track.blockers_of(t, tasks)
        out.append({
            "id": t.id, "title": t.title, "owner": t.owner or "unassigned",
            "area": t.area, "milestone": t.milestone, "status": t.status,
            "depends_on": t.list_field("depends_on"),
            "blocks": t.list_field("blocks"),
            "bench": t.bench, "started": t.started, "finished": t.finished,
            "blockers": [{"id": b.id, "owner": b.owner, "status": b.status,
                          "title": b.title} for b in blockers],
            "ready": t.status == "todo" and not blockers,
            "log": [l[2:] for l in t.log_lines],
        })
    phase, nxt, why = track.detect_phase()
    docs = [{"phase": ph, "path": rel.split("spec/", 1)[-1],
             "done": (track.ROOT / rel).exists()} for ph, rel in track.DOC_REGISTER]
    return {"tasks": out,
            "people": [{"id": k, "display": v.get("display", k),
                        "role": v.get("role", "")} for k, v in people.items()],
            "phase": {"name": phase, "next": nxt, "why": why},
            "docs": docs}


def act(tid: str, body: dict) -> dict:
    """Every mutation goes through track.py, so the UI cannot invent a rule."""
    tasks = track.load_all()
    if tid not in tasks:
        return {"error": f"no task {tid}"}
    t, who = tasks[tid], (body.get("who") or "").strip()
    if not who or who not in track.load_people():
        return {"error": "pick who you are first"}
    action = body.get("action")

    if action == "log":
        text = (body.get("text") or "").strip()
        if not text:
            return {"error": "empty note"}
        prefix = "" if t.owner == who else "comment: "
        t.append(who, prefix + text)
        t.save()
        return {"ok": True}

    if action == "assign":
        to = body.get("to", "")
        if to not in track.load_people():
            return {"error": f"unknown person {to!r}"}
        was, t.meta["owner"] = t.owner, to
        t.append(who, f"reassigned {was or 'nobody'} -> {to}")
        t.save()
        return {"ok": True}

    if action == "block":
        on = (body.get("on") or "").strip()
        if on:
            deps = t.list_field("depends_on")
            if on not in deps:
                deps.append(on)
            t.meta["depends_on"] = ", ".join(deps)
        was, t.meta["status"] = t.status, "blocked"
        why = (body.get("why") or "").strip()
        t.append(who, f"{was} -> blocked" + (f" on {on}" if on else "")
                 + (f": {why}" if why else ""))
        t.save()
        return {"ok": True}

    targets = {"start": "doing", "unblock": "doing", "review": "review", "done": "done"}
    if action not in targets:
        return {"error": f"unknown action {action!r}"}
    to = targets[action]

    if to == "doing":
        blockers = track.blockers_of(t, tasks)
        if blockers:
            return {"error": "depends on unfinished work: "
                    + ", ".join(f"{b.id} ({b.owner}, {b.status})" for b in blockers)}
        if not t.started:
            t.meta["started"] = track.now()
    if to == "done":
        t.meta["finished"] = track.now()

    was, t.meta["status"] = t.status, to
    t.append(who, f"{was} -> {to}")
    t.save()

    freed = []
    if to == "done":
        for x in tasks.values():
            if tid in x.list_field("depends_on") and x.status == "todo":
                if not [b for b in track.blockers_of(x, tasks) if b.id != tid]:
                    freed.append({"id": x.id, "title": x.title, "owner": x.owner})
    return {"ok": True, "unblocks": freed}


# ---------------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
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
            return self._send(200, json.dumps(snapshot()))
        self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if not self.path.startswith("/api/task/"):
            return self._send(404, json.dumps({"error": "not found"}))
        tid = self.path.split("/api/task/", 1)[1]
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, json.dumps({"error": "bad request"}))
        with LOCK:
            result = act(tid, body)
        self._send(400 if "error" in result else 200, json.dumps(result))


LOCK = threading.Lock()

PAGE = r"""<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Board</title>
<style>
:root{--bg:#fbfbfd;--panel:#fff;--fg:#16161a;--dim:#71717a;--line:#e7e7ec;
--v:#6346E6;--todo:#a1a1aa;--doing:#2f6fd0;--blocked:#c8452f;--review:#c9942a;--done:#2e9e5b}
@media(prefers-color-scheme:dark){:root{--bg:#0f0f11;--panel:#17171a;--fg:#ececf0;
--dim:#8b8b95;--line:#26262b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:14px/1.5 ui-sans-serif,system-ui,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--panel);
border-bottom:1px solid var(--line);padding:14px 20px}
.top{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
h1{font-size:16px;margin:0;font-weight:650;letter-spacing:-.01em}
.grow{flex:1}
select,input,button,textarea{font:inherit;color:inherit;background:var(--panel);
border:1px solid var(--line);border-radius:8px;padding:6px 10px}
input:focus,select:focus,textarea:focus{outline:2px solid var(--v);outline-offset:-1px}
button{cursor:pointer}
button.p{background:var(--v);color:#fff;border-color:var(--v);font-weight:550}
button:disabled{opacity:.4;cursor:not-allowed}
.bar{display:flex;height:6px;border-radius:3px;overflow:hidden;background:var(--line);margin-top:12px}
.bar i{display:block}
.tabs{display:flex;gap:4px;margin-top:12px}
.tabs button{border:none;background:none;padding:6px 12px;border-radius:8px;color:var(--dim)}
.tabs button.on{background:var(--v);color:#fff;font-weight:550}
main{padding:20px;max-width:1500px;margin:0 auto}
.cols{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
@media(max-width:1100px){.cols{grid-template-columns:1fr 1fr}}
.col h2{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
margin:0 0 8px;display:flex;justify-content:space-between}
.card{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:9px;padding:9px 11px;margin-bottom:7px;cursor:pointer}
.card:hover{border-color:var(--v)}
.card.doing{border-left-color:var(--doing)}.card.blocked{border-left-color:var(--blocked)}
.card.review{border-left-color:var(--review)}.card.done{border-left-color:var(--done);opacity:.55}
.card.ready{border-left-color:var(--v)}
.card b{font:600 11.5px ui-monospace,Menlo,Consolas,monospace;color:var(--v)}
.card p{margin:3px 0 0;font-size:13px}
.meta{margin-top:5px;font-size:11.5px;color:var(--dim);display:flex;gap:8px;flex-wrap:wrap}
.pill{background:var(--line);padding:1px 7px;border-radius:20px;font-size:11px}
.warn{color:var(--blocked)}
.rows .card{border-left-width:3px}
#drawer{position:fixed;inset:0 0 0 auto;width:min(520px,100%);background:var(--panel);
border-left:1px solid var(--line);transform:translateX(100%);transition:.16s;
overflow:auto;padding:22px;z-index:10;box-shadow:-18px 0 44px #0002}
#drawer.on{transform:none}
#drawer h3{margin:0;font-size:17px}
kbd{font:11.5px ui-monospace,Menlo,Consolas,monospace;background:var(--line);
padding:2px 6px;border-radius:5px}
.acts{display:flex;gap:7px;flex-wrap:wrap;margin:16px 0}
.log{border-top:1px solid var(--line);margin-top:16px;padding-top:12px}
.log div{font-size:12.5px;padding:5px 0;border-bottom:1px dashed var(--line)}
.log time{color:var(--dim);font:11.5px ui-monospace,Menlo,Consolas,monospace}
.who{color:var(--v);font-weight:600}
.dim{color:var(--dim)}
.empty{color:var(--dim);font-size:12.5px;padding:10px 2px}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:var(--fg);
color:var(--bg);padding:10px 18px;border-radius:9px;font-size:13px;opacity:0;
transition:.2s;pointer-events:none;z-index:20;max-width:80vw}
#toast.on{opacity:1}
.pipe{display:flex;gap:6px;align-items:center;margin-top:10px;flex-wrap:wrap;font-size:12px}
.pipe .step{padding:3px 10px;border-radius:20px;background:var(--line);color:var(--dim);white-space:nowrap}
.pipe .step.done{background:var(--done);color:#fff}
.pipe .step.on{background:var(--v);color:#fff;font-weight:600}
.pipe .sep{color:var(--line)}
.pipe .why{color:var(--dim);margin-left:6px}
</style>

<header>
  <div class=top>
    <h1 id=proj>Board</h1>
    <span class=dim id=count></span>
    <span class=grow></span>
    <input id=q placeholder="Search id or title" size=22>
    <select id=fOwner></select>
    <select id=fMile><option value="">All milestones</option></select>
    <span class=dim>I am</span>
    <select id=me></select>
  </div>
  <div class=pipe id=pipe></div>
  <div class=bar id=bar></div>
  <div class=tabs>
    <button data-v=board class=on>Board</button>
    <button data-v=ready>Ready to start</button>
    <button data-v=blocked>Waiting on someone</button>
    <button data-v=mine>Mine</button>
  </div>
</header>

<main id=main></main>
<div id=drawer></div>
<div id=toast></div>

<script>
const S={tasks:[],people:[],view:'board',q:'',owner:'',mile:'',me:localStorage.me||'',sel:null};
const $=s=>document.querySelector(s);
const ORDER=['todo','doing','blocked','review','done'];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function toast(m,bad){const t=$('#toast');t.textContent=m;t.style.background=bad?'var(--blocked)':'';
  t.style.color=bad?'#fff':'';t.classList.add('on');clearTimeout(t._);t._=setTimeout(()=>t.classList.remove('on'),3200);}

async function load(){
  const r=await fetch('/api/state');const d=await r.json();
  S.tasks=d.tasks;S.people=d.people;S.phase=d.phase;S.docs=d.docs||[];
  const opts=p=>p.map(x=>`<option value="${x.id}">${esc(x.display)}</option>`).join('');
  if(!$('#me').options.length){
    $('#me').innerHTML='<option value="">choose…</option>'+opts(S.people);
    $('#me').value=S.me;
    $('#fOwner').innerHTML='<option value="">Everyone</option>'+opts(S.people)
      +'<option value="unassigned">Unassigned</option>';
    const ms=[...new Set(S.tasks.map(t=>t.milestone))].filter(Boolean).sort();
    $('#fMile').innerHTML='<option value="">All milestones</option>'
      +ms.map(m=>`<option>${esc(m)}</option>`).join('');
  }
  render();
}

const match=t=>(!S.q||(t.id+' '+t.title).toLowerCase().includes(S.q.toLowerCase()))
  &&(!S.owner||t.owner===S.owner)&&(!S.mile||t.milestone===S.mile);

function card(t){
  const cls=t.status==='todo'&&t.ready?'ready':t.status;
  const bl=t.blockers.length?`<span class=warn>waiting on ${t.blockers.map(b=>b.id).join(', ')}</span>`:'';
  return `<div class="card ${cls}" data-id="${t.id}"><b>${esc(t.id)}</b>
    <p>${esc(t.title)}</p><div class=meta><span class=pill>${esc(t.owner)}</span>
    <span>${esc(t.milestone)}</span>${bl}</div></div>`;
}

const PIPE=['Discover','Define','Design','Architect','Feasibility','Build'];
const PHASE_AT={'Pre-Discover':0,'Discovering':0,'Discover done':1,'Define done':2,
  'Design done':3,'Architect done':4,'Feasibility done':5,'Building':5};

function renderPipe(){
  const el=$('#pipe'); if(!el) return;
  const ph=S.phase||{name:'Pre-Discover',next:'/keel',why:''};
  const cur=PHASE_AT[ph.name]??0;
  const dn=(S.docs||[]).filter(x=>x.done).length, tot=(S.docs||[]).length;
  const steps=PIPE.map((s,i)=>{
    const cls=i<cur?'done':(i===cur?'on':'');
    return `<span class="step ${cls}">${s}</span>`;
  }).join('<span class=sep>›</span>');
  el.innerHTML=steps+`<span class=why>${esc(ph.why||'')} · next <b>${esc(ph.next||'')}</b>`
    +(tot?` · docs ${dn}/${tot}`:'')+`</span>`;
}

function render(){
  const ts=S.tasks.filter(match), done=S.tasks.filter(t=>t.status==='done').length;
  $('#count').textContent=`${done} of ${S.tasks.length} done`;
  renderPipe();
  $('#bar').innerHTML=ORDER.map(s=>{const n=S.tasks.filter(t=>t.status===s).length;
    return n?`<i style="width:${100*n/S.tasks.length}%;background:var(--${s})" title="${s}: ${n}"></i>`:''}).join('');

  let h='';
  if(S.view==='board'){
    h='<div class=cols>'+ORDER.map(s=>{const g=ts.filter(t=>t.status===s);
      return `<div class=col><h2>${s}<span>${g.length}</span></h2>${
        g.map(card).join('')||'<div class=empty>nothing</div>'}</div>`}).join('')+'</div>';
  } else if(S.view==='ready'){
    const g=ts.filter(t=>t.ready);
    h=`<div class=rows>${g.map(card).join('')||'<div class=empty>Nothing is ready. Check what you are waiting on.</div>'}</div>`;
  } else if(S.view==='blocked'){
    const pairs=[];
    S.tasks.forEach(t=>{if(t.status!=='done')t.blockers.forEach(b=>{if(b.owner!==t.owner)pairs.push([b,t])})});
    const by={};pairs.forEach(([b,t])=>{(by[b.owner]=by[b.owner]||[]).push([b,t])});
    h=Object.keys(by).sort().map(o=>`<h2 style="margin:18px 0 8px;font-size:13px">
      <b>${esc(o)}</b> <span class=dim>is holding up ${by[o].length}</span></h2>
      <div class=rows>${by[o].map(([b,t])=>`<div class="card ${b.status}" data-id="${b.id}">
        <b>${esc(b.id)}</b><p>${esc(b.title)}</p>
        <div class=meta><span class=warn>blocks ${esc(t.id)}</span>
        <span class=pill>${esc(t.owner)}</span></div></div>`).join('')}</div>`).join('')
      ||'<div class=empty>Nobody is waiting on anybody.</div>';
  } else {
    const g=ts.filter(t=>t.owner===S.me);
    h=ORDER.filter(s=>s!=='done').map(s=>{const gg=g.filter(t=>t.status===s);
      return gg.length?`<h2 style="margin:18px 0 8px;font-size:13px;text-transform:uppercase">${s}</h2>
        <div class=rows>${gg.map(card).join('')}</div>`:''}).join('')
      ||'<div class=empty>Pick who you are, top right.</div>';
  }
  $('#main').innerHTML=h;
  if(S.sel)drawer(S.sel);
}

function drawer(id){
  const t=S.tasks.find(x=>x.id===id);const d=$('#drawer');
  if(!t){d.classList.remove('on');S.sel=null;return}
  S.sel=id;
  const can=a=>({start:['todo','blocked'],review:['doing'],done:['doing','review'],
                 block:['todo','doing','review']}[a]||[]).includes(t.status);
  const dep=t.blockers.length?`<p class=warn style="margin:10px 0 0">Waiting on ${
    t.blockers.map(b=>`<kbd>${esc(b.id)}</kbd> ${esc(b.owner)}`).join(', ')}</p>`:'';
  const bl=t.blocks.length?`<p class=dim style="margin:6px 0 0">Blocks ${
    t.blocks.map(x=>`<kbd>${esc(x)}</kbd>`).join(' ')}</p>`:'';
  d.innerHTML=`<div style="display:flex;gap:10px;align-items:start">
      <div style=flex:1><kbd>${esc(t.id)}</kbd> <span class=pill>${esc(t.status)}</span>
      <span class=pill>${esc(t.milestone)}</span> <span class=pill>${esc(t.owner)}</span>
      <h3 style="margin:9px 0 0">${esc(t.title)}</h3></div>
      <button onclick="drawer(null)">close</button></div>
    ${dep}${bl}
    ${t.started?`<p class=dim style="margin:8px 0 0">started ${esc(t.started)}</p>`:''}
    ${t.finished?`<p class=dim style="margin:2px 0 0">finished ${esc(t.finished)}</p>`:''}
    <div class=acts>
      <button class=p onclick="go('start')" ${can('start')?'':'disabled'}>Start</button>
      <button onclick="go('review')" ${can('review')?'':'disabled'}>Ready for review</button>
      <button onclick="go('done')" ${can('done')?'':'disabled'}>Done</button>
      <button onclick="doBlock()" ${can('block')?'':'disabled'}>Block…</button>
      ${t.status==='blocked'?'<button onclick="go(\'unblock\')">Unblock</button>':''}
    </div>
    <textarea id=note rows=2 style=width:100% placeholder="Add a note. Anyone can; it is attributed."></textarea>
    <button style="margin-top:7px" onclick="addNote()">Add note</button>
    <div class=log>${t.log.slice().reverse().map(l=>{
      const p=l.split(' · ');
      return `<div><time>${esc(p[0]||'')}</time> <span class=who>${esc(p[1]||'')}</span>
        ${esc(p.slice(2).join(' · '))}</div>`}).join('')||'<div class=empty>no log yet</div>'}</div>`;
  d.classList.add('on');
}

async function post(id,body){
  if(!S.me){toast('Pick who you are first, top right.',1);return null}
  const r=await fetch('/api/task/'+id,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,who:S.me})});
  const d=await r.json();
  if(d.error){toast(d.error,1);return null}
  await load();return d;
}
async function go(a){
  const d=await post(S.sel,{action:a});
  if(!d)return;
  if(d.unblocks&&d.unblocks.length)
    toast('Done. Unblocks '+d.unblocks.map(u=>u.id+' ('+u.owner+')').join(', ')+'. Say so in NOW.md.');
  else toast('Updated.');
}
async function doBlock(){
  const on=prompt('Blocked on which task id? (blank if not a task)')||'';
  const why=prompt('Why?')||'';
  if(await post(S.sel,{action:'block',on:on.trim().toUpperCase(),why}))toast('Blocked.');
}
async function addNote(){
  const el=$('#note');const text=el.value.trim();if(!text)return;
  if(await post(S.sel,{action:'log',text})){el.value='';toast('Noted.')}
}

document.addEventListener('click',e=>{
  const c=e.target.closest('.card');if(c)drawer(c.dataset.id);
  const b=e.target.closest('.tabs button');
  if(b){S.view=b.dataset.v;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));render()}
});
$('#q').oninput=e=>{S.q=e.target.value;render()};
$('#fOwner').onchange=e=>{S.owner=e.target.value;render()};
$('#fMile').onchange=e=>{S.mile=e.target.value;render()};
$('#me').onchange=e=>{S.me=localStorage.me=e.target.value;render()};
document.addEventListener('keydown',e=>{if(e.key==='Escape')drawer(null)});
load();setInterval(load,15000);
</script>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=7777)
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    if not track.TASKS.exists():
        sys.exit("no tracker/tasks yet. Seed it first.")

    url = f"http://127.0.0.1:{a.port}/"
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    n = len(list(track.TASKS.glob("*.md")))
    print(f"Board  {url}   {n} tasks")
    print("Reads and writes tracker/tasks/. Commit your changes like any others.")
    print("Ctrl-C to stop.")
    if not a.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
