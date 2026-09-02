#!/usr/bin/env python3
"""Progress tracker: one file per task, in git.

Why a file-per-task in git and not a web app: it works on day one with no
database, no hosting and no auth; git gives history, timestamps and
attribution for free; Claude Code can read and write it natively; and two
people editing different tasks never conflict.

Data lives in tracker/tasks/<ID>.md, one file per task: a small header, then
an append-only log. People live in tracker/people.toml.

    track status                     what is done, doing, blocked, in review
    track phase                      which pipeline phase, and the next command
    track docs                       the pipeline document set, as a live checklist
    track next [--for NAME]          tasks you can start now, deps satisfied
    track blocked                    who is waiting on whom, across people
    track mine [--for NAME]          your board
    track show <ID>                  one task in full, with its log

    track start <ID>                 todo   -> doing
    track review <ID>                doing  -> review
    track done <ID>                  review -> done, and reports what it unblocks
    track block <ID> --on <ID> "why"
    track unblock <ID> ["note"]
    track log <ID> "what happened"   an entry on your own task
    track comment <ID> "..."         an entry on anyone's task
    track assign <ID> NAME
    track add <ID> --title T --owner N --area A --milestone M [--depends A,B]

    track render                     writes tracker/build/index.html
    track check                      structural problems fail, staleness warns

Every state change and every log line is timestamped and attributed. Identity
comes from --as, then $TRACK_USER, then git config user.name via people.toml.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "tracker"
TASKS = TRACKER / "tasks"
PEOPLE = TRACKER / "people.toml"
BUILD = TRACKER / "build"

STATUSES = ("todo", "doing", "blocked", "review", "done")
OPEN = ("todo", "doing", "blocked", "review")


# Timestamps use this machine's local timezone; set TRACK_TZ (e.g. "+05:30")
# to pin a team-wide offset instead.
def _tz():
    spec = os.environ.get("TRACK_TZ", "").strip()
    m = re.match(r"^([+-])(\d{1,2}):?(\d{2})$", spec)
    if m:
        sign = 1 if m.group(1) == "+" else -1
        return dt.timezone(
            sign * dt.timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
        )
    return dt.datetime.now().astimezone().tzinfo


TZ = _tz()


def _project_name() -> str:
    """The project's display name: the `Project:` line in NOW.md if present,
    else the repository folder's name."""
    now_md = ROOT / "docs" / "10-STATUS" / "NOW.md"
    if now_md.exists():
        for line in now_md.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\*{0,2}Project\*{0,2}\s*:\s*(.+?)\s*$", line.strip())
            if m:
                return m.group(1)
    return ROOT.name


PROJECT = _project_name()

LIST_FIELDS = ("depends_on", "blocks")
FIELDS = (
    "id",
    "title",
    "owner",
    "area",
    "milestone",
    "status",
    "depends_on",
    "blocks",
    "bench",
    "started",
    "finished",
)


# ----------------------------------------------------------------- utilities


def now() -> str:
    return dt.datetime.now(TZ).strftime("%Y-%m-%dT%H:%M%z")


def parse_ts(s: str):
    try:
        return dt.datetime.strptime(s.strip(), "%Y-%m-%dT%H:%M%z")
    except (ValueError, AttributeError):
        return None


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_people() -> dict:
    """name -> {display, role}. Deliberately trivial to extend: add a block."""
    people, cur = {}, None
    if not PEOPLE.exists():
        return people
    for line in PEOPLE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"^\[people\.([A-Za-z0-9_-]+)\]$", line)
        if m:
            cur = m.group(1)
            people[cur] = {"display": cur, "role": ""}
            continue
        if cur and "=" in line:
            k, v = (p.strip() for p in line.split("=", 1))
            people[cur][k] = v.strip().strip('"')
    return people


def whoami(explicit: str | None) -> str:
    people = load_people()
    if explicit:
        if explicit not in people:
            die(f"unknown person {explicit!r}. Known: {', '.join(people) or 'none'}")
        return explicit
    env = os.environ.get("TRACK_USER")
    if env and env in people:
        return env
    git_name = (
        subprocess.run(
            ["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True
        )
        .stdout.strip()
        .lower()
    )
    for key, meta in people.items():
        if key in git_name or meta.get("display", "").lower() in git_name:
            return key
    # A one-person roster leaves nothing to disambiguate: it's you.
    if len(people) == 1:
        return next(iter(people))
    if not people:
        die(
            "the roster is empty. Add yourself to tracker/people.toml "
            "(copy a block from people.example.toml), then try again."
        )
    die(
        f"cannot tell which roster entry is you ({', '.join(people)}). "
        f"Run the command again with --as <name>, or set TRACK_USER, or make "
        f"sure your git user.name matches your entry in tracker/people.toml."
    )


# --------------------------------------------------------------------- model


class Task:
    def __init__(self, path: Path):
        self.path = path
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            die(f"{path.name}: missing header")
        _, header, body = raw.split("---", 2)
        self.meta = {f: "" for f in FIELDS}
        for line in header.strip().splitlines():
            if ":" not in line:
                continue
            k, v = (p.strip() for p in line.split(":", 1))
            self.meta[k] = v
        self.body = body.lstrip("\n")

    # convenience accessors
    def __getattr__(self, name):
        if name in FIELDS:
            return self.meta.get(name, "")
        raise AttributeError(name)

    def list_field(self, name) -> list[str]:
        return [x.strip() for x in self.meta.get(name, "").split(",") if x.strip()]

    @property
    def log_lines(self) -> list[str]:
        return [line for line in self.body.splitlines() if line.startswith("- 20")]

    @property
    def last_activity(self):
        for line in reversed(self.log_lines):
            ts = parse_ts(line[2:].split(" · ")[0])
            if ts:
                return ts
        return None

    def append(self, who: str, text: str):
        if "## Log" not in self.body:
            self.body = self.body.rstrip() + "\n\n## Log\n"
        self.body = self.body.rstrip() + f"\n- {now()} · {who} · {text}\n"

    def save(self):
        header = "\n".join(f"{f}: {self.meta.get(f, '')}" for f in FIELDS)
        self.path.write_text(
            f"---\n{header}\n---\n\n{self.body.rstrip()}\n", encoding="utf-8"
        )


def load_all() -> dict[str, Task]:
    if not TASKS.exists():
        return {}
    return {p.stem: Task(p) for p in sorted(TASKS.glob("*.md"))}


def get(tasks, tid) -> Task:
    if tid not in tasks:
        die(f"no task {tid!r}. `track status` lists them.")
    return tasks[tid]


def blockers_of(t: Task, tasks) -> list[Task]:
    """Dependencies that are not done yet."""
    return [
        tasks[d]
        for d in t.list_field("depends_on")
        if d in tasks and tasks[d].status != "done"
    ]


# -------------------------------------------------------------------- output

C = {
    "done": "\033[32m",
    "doing": "\033[36m",
    "blocked": "\033[31m",
    "review": "\033[33m",
    "todo": "\033[90m",
    "0": "\033[0m",
    "b": "\033[1m",
}


def paint(s, key):
    return f"{C.get(key, '')}{s}{C['0']}" if sys.stdout.isatty() else s


def row(t: Task, tasks, show_owner=True):
    owner = f"  {t.owner:<9}" if show_owner else ""
    blockers = blockers_of(t, tasks)
    note = ""
    if t.status == "blocked" or blockers:
        note = (
            "  <- waiting on " + ", ".join(f"{b.id} ({b.owner})" for b in blockers)
            if blockers
            else "  <- blocked"
        )
    badge = paint(f"{t.status.upper():<8}", t.status)
    return f"  {badge}{owner}  {t.id:<8}  {t.title[:52]}{note}"


# ------------------------------------------------------------------ commands


def cmd_status(a):
    tasks = load_all()
    if not tasks:
        die(
            "no tasks yet. Run /plan to load the build roadmap into tasks, "
            'or add one: python tools/track.py --as <you> add <ID> --title "..."'
        )
    counts = {s: sum(1 for t in tasks.values() if t.status == s) for s in STATUSES}
    total = len(tasks)
    pct = round(100 * counts["done"] / total) if total else 0
    print(
        f"\n{paint(PROJECT, 'b')}   {counts['done']}/{total} done ({pct}%)   "
        + "  ".join(f"{paint(s, s)} {counts[s]}" for s in STATUSES)
    )

    for state, label in (
        ("blocked", "Blocked"),
        ("review", "In review"),
        ("doing", "In flight"),
    ):
        group = [t for t in tasks.values() if t.status == state]
        if group:
            print(f"\n{paint(label, 'b')}")
            for t in group:
                print(row(t, tasks))

    ready = [
        t for t in tasks.values() if t.status == "todo" and not blockers_of(t, tasks)
    ]
    if ready:
        print(f"\n{paint('Ready to start', 'b')}  (dependencies satisfied)")
        for t in sorted(ready, key=lambda x: (x.milestone, x.id))[:12]:
            print(row(t, tasks))
        if len(ready) > 12:
            print(f"    ... and {len(ready) - 12} more. `track next --for NAME`")
    print()


def cmd_next(a):
    tasks = load_all()
    who = a.for_ or None
    ready = [
        t
        for t in tasks.values()
        if t.status == "todo"
        and not blockers_of(t, tasks)
        and (not who or t.owner == who)
    ]
    if not ready:
        print("nothing ready. `track blocked` shows what is in the way.")
        return
    print(f"\n{paint('Ready now' + (f' for {who}' if who else ''), 'b')}")
    for t in sorted(ready, key=lambda x: (x.milestone, x.id)):
        print(row(t, tasks, show_owner=not who))
    print()


def cmd_blocked(a):
    """The cross-person view: whose unfinished work is holding whom up."""
    tasks = load_all()
    waiting = {}
    for t in tasks.values():
        if t.status == "done":
            continue
        for b in blockers_of(t, tasks):
            if b.owner != t.owner:
                waiting.setdefault(b.owner, []).append((b, t))
    if not waiting:
        print("\nNobody is waiting on anybody. \n")
        return
    print(f"\n{paint('Cross-person dependencies', 'b')}")
    for owner, pairs in sorted(waiting.items()):
        print(f"\n  {paint(owner, 'b')} is holding up {len(pairs)}:")
        for b, t in sorted(pairs, key=lambda p: p[0].id):
            print(
                f"      {b.id} ({paint(b.status, b.status)})  ->  "
                f"{t.id} {t.title[:40]}  [{t.owner}]"
            )
    print()


def cmd_mine(a):
    tasks = load_all()
    who = a.for_ or whoami(a.as_)
    mine = [t for t in tasks.values() if t.owner == who]
    print(
        f"\n{paint(who + chr(39) + 's board', 'b')}   "
        f"{sum(1 for t in mine if t.status == 'done')}/{len(mine)} done"
    )
    for state in ("blocked", "review", "doing", "todo"):
        group = [t for t in mine if t.status == state]
        if not group:
            continue
        print(f"\n  {paint(state.upper(), state)}")
        for t in sorted(group, key=lambda x: (x.milestone, x.id))[:20]:
            print(row(t, tasks, show_owner=False))
    print()


def cmd_show(a):
    t = get(load_all(), a.id)
    print(f"\n{paint(t.id + '  ' + t.title, 'b')}")
    for f in (
        "owner",
        "area",
        "milestone",
        "status",
        "depends_on",
        "blocks",
        "bench",
        "started",
        "finished",
    ):
        if t.meta.get(f):
            print(f"  {f:<12} {t.meta[f]}")
    print(f"\n{t.body.rstrip()}\n")


GUARDS = {
    "doing": ("todo", "blocked"),
    "review": ("doing",),
    "done": ("doing", "review"),
}


def apply_transition(tasks, t, to, who, extra=None):
    """The task state machine. One source of truth, called by both the CLI and
    the board, so a rule can never live in two places and drift.

    Returns ``(error, freed)``: ``error`` is a message string if the transition
    is not allowed (the caller decides how to surface it), else ``None``; ``freed``
    is the list of tasks this completion unblocks.
    """
    guard = GUARDS.get(to)
    if guard and t.status not in guard:
        return f"{t.id} is {t.status}, expected one of {', '.join(guard)}", []
    if to == "doing":
        blockers = blockers_of(t, tasks)
        if blockers:
            return (
                "depends on unfinished work: "
                + ", ".join(f"{b.id} ({b.owner}, {b.status})" for b in blockers)
            ), []
        if not t.started:
            t.meta["started"] = now()
    if to == "done":
        t.meta["finished"] = now()
    was, t.meta["status"] = t.status, to
    t.append(who, extra or f"{was} -> {to}")
    t.save()
    freed = []
    if to == "done":
        freed = [
            x
            for x in tasks.values()
            if t.id in x.list_field("depends_on")
            and x.status == "todo"
            and not [b for b in blockers_of(x, tasks) if b.id != t.id]
        ]
    return None, freed


def _transition(a, to, guard=None, extra=None):
    tasks = load_all()
    t = get(tasks, a.id)
    who = whoami(a.as_)
    was = t.status
    error, freed = apply_transition(tasks, t, to, who, extra=extra)
    if error:
        die(error if error.startswith(t.id) else f"{t.id} {error}")
    print(f"{t.id}: {was} -> {paint(to, to)}")
    if freed:
        print("\n  This unblocks:")
        for x in freed:
            print(f"      {x.id}  {x.title[:46]}  [{x.owner}]")
        print("\n  Say so in docs/10-STATUS/NOW.md. Do not wait to be asked.")


def cmd_start(a):
    _transition(a, "doing", guard=("todo", "blocked"))


def cmd_review(a):
    _transition(a, "review", guard=("doing",))


def cmd_done(a):
    _transition(a, "done", guard=("doing", "review"))


def cmd_block(a):
    tasks = load_all()
    t = get(tasks, a.id)
    if a.on:
        deps = t.list_field("depends_on")
        for d in a.on.split(","):
            d = d.strip()
            if d and d not in deps:
                deps.append(d)
        t.meta["depends_on"] = ", ".join(deps)
    was, t.meta["status"] = t.status, "blocked"
    t.append(
        whoami(a.as_),
        f"{was} -> blocked"
        + (f" on {a.on}" if a.on else "")
        + (f": {a.why}" if a.why else ""),
    )
    t.save()
    print(f"{t.id}: {was} -> {paint('blocked', 'blocked')}")


def cmd_unblock(a):
    _transition(
        a,
        "doing",
        guard=("blocked",),
        extra="unblocked" + (f": {a.note}" if a.note else ""),
    )


def cmd_log(a):
    tasks = load_all()
    t = get(tasks, a.id)
    who = whoami(a.as_)
    if t.owner and t.owner != who:
        print(f"note: {t.id} is {t.owner}'s. Recording this as a comment.")
    t.append(who, a.message)
    t.save()
    print(f"{t.id}: logged.")


def cmd_comment(a):
    tasks = load_all()
    t = get(tasks, a.id)
    t.append(whoami(a.as_), f"comment: {a.message}")
    t.save()
    print(f"{t.id}: comment added.")


def cmd_assign(a):
    tasks = load_all()
    t = get(tasks, a.id)
    people = load_people()
    if a.to not in people:
        die(f"unknown person {a.to!r}")
    was, t.meta["owner"] = t.owner, a.to
    t.append(whoami(a.as_), f"reassigned {was or 'nobody'} -> {a.to}")
    t.save()
    print(f"{t.id}: {was or 'nobody'} -> {a.to}")


def cmd_add(a):
    TASKS.mkdir(parents=True, exist_ok=True)
    p = TASKS / f"{a.id}.md"
    if p.exists():
        die(f"{a.id} already exists")
    meta = {
        "id": a.id,
        "title": a.title,
        "owner": a.owner,
        "area": a.area,
        "milestone": a.milestone,
        "status": "todo",
        "depends_on": a.depends or "",
        "blocks": "",
        "bench": a.bench or "",
        "started": "",
        "finished": "",
    }
    header = "\n".join(f"{f}: {meta.get(f, '')}" for f in FIELDS)
    p.write_text(
        f"---\n{header}\n---\n\n## Log\n- {now()} · {whoami(a.as_)} · created\n",
        encoding="utf-8",
    )
    print(f"created {p.relative_to(ROOT)}")


def cmd_check(a):
    """CI gate. Rules that a document cannot enforce and a person will forget."""
    tasks = load_all()
    if not tasks:
        print("check: no tasks. skipping.")
        return 0
    fails, warns = [], []
    today = dt.datetime.now(TZ)

    for t in tasks.values():
        if t.status not in STATUSES:
            fails.append(f"{t.id}: unknown status {t.status!r}")
        for d in t.list_field("depends_on"):
            if d not in tasks:
                fails.append(f"{t.id}: depends on {d}, which does not exist")
        if t.status == "done" and not t.finished:
            fails.append(f"{t.id}: done with no finished timestamp")
        # a done task whose dependency is not done means the order was broken
        if t.status == "done":
            open_deps = [b.id for b in blockers_of(t, tasks)]
            if open_deps:
                fails.append(
                    f"{t.id}: done, but depends on unfinished " + ", ".join(open_deps)
                )
        if t.status in ("doing", "blocked"):
            last = t.last_activity
            if last is None:
                fails.append(f"{t.id}: {t.status} with an empty log")
            else:
                idle = (today - last).days
                if idle > a.max_idle_days:
                    # A warning, not a failure. Staleness is a nudge to the person,
                    # not a reason to stop a colleague landing unrelated work.
                    warns.append(
                        f"{t.id}: {t.status} for {idle} days with no update. "
                        f"Log progress, block it, or hand it over."
                    )
        if t.status == "doing" and not t.started:
            warns.append(f"{t.id}: doing with no started timestamp")

    in_flight = {}
    for t in tasks.values():
        if t.status == "doing":
            in_flight.setdefault(t.owner, []).append(t.id)
    for owner, ids in in_flight.items():
        if len(ids) > a.max_in_flight:
            warns.append(
                f"{owner} has {len(ids)} tasks in flight "
                f"({', '.join(ids)}). More than {a.max_in_flight} usually "
                "means none of them is moving."
            )

    for w in warns:
        print(f"warn  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    if fails:
        print(f"\ntracker check failed: {len(fails)} problem(s).")
        print("The tracker is the shared memory between two people and two AI")
        print("sessions. Stale means somebody is working from a wrong picture.")
        return 1
    print(f"tracker check ok: {len(tasks)} tasks, {len(warns)} warning(s).")
    return 0


SPEC = ROOT / "spec"
DOCS = ROOT / "docs"

# The document set the pipeline produces, in order, each tied to the phase that
# writes it and the shape(s) it applies to: "all" (company and project), "company"
# (skipped for a project), or "project". `track docs` checks these against disk.
DOC_REGISTER = [
    ("Discover", "spec/04-Business/PRIOR-ART.md", "all"),
    ("Discover", "spec/01-Company/CONCEPT.md", "project"),
    ("Discover", "spec/01-Company/COMPANY-NARRATIVE.md", "company"),
    ("Discover", "spec/01-Company/POSITIONING.md", "company"),
    ("Discover", "spec/01-Company/ONE-PAGER.md", "company"),
    ("Discover", "spec/04-Business/MARKET-ANALYSIS.md", "company"),
    ("Discover", "spec/04-Business/COMPETITOR-ANALYSIS.md", "company"),
    ("Discover", "spec/04-Business/BUSINESS-MODEL.md", "company"),
    ("Discover", "spec/04-Business/UNIT-ECONOMICS.md", "company"),
    ("Discover", "spec/04-Business/GTM.md", "company"),
    ("Discover", "spec/04-Business/DEFENSIBILITY.md", "company"),
    ("Discover", "spec/01-Company/VISION-MISSION-VALUES.md", "company"),
    ("Discover", "spec/01-Company/HOW-WE-PITCH.md", "company"),
    ("Discover", "spec/05-Finance/COST-TO-RUN.md", "company"),
    ("Discover", "spec/05-Finance/FINANCIAL-MODEL.md", "company"),
    ("Discover", "spec/05-Finance/FUNDRAISE-ASK.md", "company"),
    ("Define", "spec/02-Product/USER-INSIGHT.md", "all"),
    ("Define", "spec/02-Product/PRD.md", "all"),
    ("Define", "spec/02-Product/USER-STORIES.md", "all"),
    ("Define", "spec/02-Product/SUCCESS-METRICS.md", "all"),
    ("Define", "spec/02-Product/FLOWS.md", "all"),
    ("Define", "spec/02-Product/PRODUCT-ROADMAP.md", "all"),
    ("Define", "spec/02-Product/REAL-WORLD-SCENARIOS.md", "all"),
    ("Design", "spec/06-Design/DESIGN-BRIEF.md", "all"),
    ("Design", "spec/06-Design/DESIGN-SYSTEM.md", "all"),
    ("Architect", "spec/03-Technical/TECHNICAL-DESIGN.md", "all"),
    ("Architect", "spec/03-Technical/TECH-STACK.md", "all"),
    ("Architect", "spec/03-Technical/DATA-MODEL.md", "all"),
    ("Architect", "spec/03-Technical/SECURITY-PRIVACY.md", "all"),
    ("Architect", "spec/03-Technical/INFRA-DEVOPS.md", "all"),
    ("Architect", "spec/03-Technical/TOOLS-AND-ACCOUNTS.md", "all"),
    ("Architect", "spec/03-Technical/BUILD-ROADMAP.md", "all"),
    ("Architect", "spec/03-Technical/SETUP-RUNBOOK.md", "all"),
]


def detect_mode() -> str:
    """company | project | experiment, from a Mode: line in NOW.md, else inferred."""
    now = ROOT / "docs" / "10-STATUS" / "NOW.md"
    if now.exists():
        m = re.search(
            r"(?im)^\**\s*Mode\s*[:=]?\s*\**\s*(company|project|experiment)",
            now.read_text(encoding="utf-8", errors="ignore"),
        )
        if m:
            return m.group(1).lower()
    # No marker: infer from what's on disk. Company docs present -> company.
    if (ROOT / "spec" / "04-Business" / "MARKET-ANALYSIS.md").exists():
        return "company"
    if (ROOT / "spec" / "01-Company" / "CONCEPT.md").exists():
        return "project"
    return "company"  # safe default: show the full set until /keel sets the shape


def register_for(mode: str) -> list[tuple[str, str]]:
    """The (group, path) rows that apply to this shape."""
    exp = {"company", "all"} if mode == "company" else {"project", "all"}
    return [(g, rel) for (g, rel, applies) in DOC_REGISTER if applies in exp]


def _exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def _has_audit(kind: str) -> bool:
    d = DOCS / "50-AUDITS"
    return d.exists() and any(kind in p.name for p in d.glob("*.md"))


def detect_phase() -> tuple[str, str, str]:
    """Return (phase, next command, one-line reason), from what exists on disk.

    This is the single source of truth the /status and /next commands lean on, so
    the phase is a fact about the repository, never a guess."""
    if load_all():
        if not _exists("tools/boundaries.json"):
            return (
                "Plan done",
                "/scaffold",
                "tasks are loaded but the repo isn't wired to the stack yet; "
                "until /scaffold runs, the code gates check nothing",
            )
        return ("Building", "/next", "the tracker has tasks; the build loop is running")
    if _has_audit("feasibility"):
        return (
            "Feasibility done",
            "/plan",
            "a feasibility audit exists but no tasks are loaded",
        )
    if _exists("spec/03-Technical/BUILD-ROADMAP.md"):
        return (
            "Architect done",
            "/feasibility",
            "the build roadmap exists but hasn't been audited",
        )
    if _exists("spec/06-Design/DESIGN-BRIEF.md"):
        return (
            "Design done",
            "/architect",
            "the design exists; the technical plan is next",
        )
    if _exists("spec/02-Product/PRD.md"):
        return (
            "Define done",
            "/design",
            "the PRD exists; design is next (or skip to /architect)",
        )
    # Discover is done when its shape-appropriate anchor doc exists.
    discover_done = _exists("spec/01-Company/CONCEPT.md") or _exists(
        "spec/01-Company/COMPANY-NARRATIVE.md"
    )
    if discover_done:
        return (
            "Discover done",
            "/define",
            "the concept / business case exists; define the product",
        )
    # The template ships README stubs in spec/; only real documents count, or
    # every fresh project would skip the '/keel: tell me your idea' step.
    if SPEC.exists() and any(p for p in SPEC.rglob("*.md") if p.name != "README.md"):
        return (
            "Discovering",
            "/discover",
            "researching what exists and how this is better",
        )
    return ("Pre-Discover", "/keel", "no documents yet; start with the idea")


def cmd_phase(a):
    phase, nxt, why = detect_phase()
    print(
        f"\n{paint('Phase', 'b')}   {paint(phase, 'doing')}   "
        f"{paint('(' + detect_mode() + ')', 'todo')}"
    )
    print(f"  {why}")
    print(f"  next: {paint(nxt, 'b')}\n")


def cmd_docs(a):
    """The doc register as a live checklist: which pipeline documents exist."""
    rows_all = register_for(detect_mode())
    by_phase: dict[str, list[tuple[str, bool]]] = {}
    for phase, rel in rows_all:
        by_phase.setdefault(phase, []).append((rel, _exists(rel)))
    have = sum(1 for _, rel in rows_all if _exists(rel))
    total = len(rows_all)
    print(
        f"\n{paint('Document set', 'b')}   {have}/{total} written   "
        f"{paint('(' + detect_mode() + ' mode)', 'todo')}"
    )
    for phase in ("Discover", "Define", "Design", "Architect"):
        rows = by_phase.get(phase, [])
        if not rows:
            continue
        done = sum(1 for _, ok in rows if ok)
        print(f"\n  {paint(phase, 'b')}  {done}/{len(rows)}")
        for rel, ok in rows:
            mark = paint("[x]", "done") if ok else paint("[ ]", "todo")
            name = rel.split("spec/", 1)[-1]
            print(f"    {mark}  {name}")
    print()


def cmd_render(a):
    tasks = load_all()
    people = load_people()
    BUILD.mkdir(parents=True, exist_ok=True)
    counts = {s: sum(1 for t in tasks.values() if t.status == s) for s in STATUSES}
    total = max(len(tasks), 1)

    def esc(s):
        return html.escape(str(s or ""))

    cross = []
    for t in tasks.values():
        if t.status == "done":
            continue
        for b in blockers_of(t, tasks):
            if b.owner != t.owner:
                cross.append((b, t))

    rows = []
    for t in sorted(tasks.values(), key=lambda x: (x.milestone, x.area, x.id)):
        bl = ", ".join(f"{b.id}" for b in blockers_of(t, tasks))
        log = t.log_lines[-1][2:] if t.log_lines else ""
        rows.append(
            f'<tr class="{esc(t.status)}"><td><code>{esc(t.id)}</code></td>'
            f"<td>{esc(t.title)}</td><td>{esc(t.owner)}</td>"
            f"<td>{esc(t.milestone)}</td>"
            f'<td><span class="s {esc(t.status)}">{esc(t.status)}</span></td>'
            f'<td class="dim">{esc(bl)}</td><td class="dim">{esc(log)}</td></tr>'
        )

    bars = "".join(
        f'<div class="seg {s}" style="width:{100 * counts[s] / total:.1f}%" title="{s}: {counts[s]}"></div>'
        for s in STATUSES
        if counts[s]
    )

    crossing = (
        "".join(
            f"<li><code>{esc(b.id)}</code> <span class='dim'>({esc(b.owner)}, {esc(b.status)})</span>"
            f" blocks <code>{esc(t.id)}</code> <span class='dim'>({esc(t.owner)})</span></li>"
            for b, t in sorted(cross, key=lambda p: p[0].id)
        )
        or "<li class='dim'>Nobody is waiting on anybody.</li>"
    )

    doc = f"""<!doctype html><meta charset=utf-8>
<title>{PROJECT}</title>
<style>
:root{{--bg:#fff;--fg:#111;--dim:#777;--line:#e6e6ea;--v:#6346E6}}
@media(prefers-color-scheme:dark){{:root{{--bg:#141416;--fg:#eee;--dim:#999;--line:#2a2a2e}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:32px;background:var(--bg);color:var(--fg);
font:15px/1.5 ui-sans-serif,system-ui,Segoe UI,sans-serif}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:14px;text-transform:uppercase;
letter-spacing:.08em;color:var(--dim);margin:32px 0 10px}}
.wrap{{max-width:1180px;margin:0 auto}}
.bar{{display:flex;height:10px;border-radius:5px;overflow:hidden;margin:14px 0 6px;background:var(--line)}}
.seg.done{{background:#2e9e5b}} .seg.doing{{background:#2f6fd0}} .seg.blocked{{background:#c8452f}}
.seg.review{{background:#c9942a}} .seg.todo{{background:var(--line)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:left;color:var(--dim);font-weight:600;padding:8px 10px;border-bottom:1px solid var(--line)}}
td{{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
tr.done td{{opacity:.5}}
.dim{{color:var(--dim);font-size:12.5px}}
code{{font:12.5px ui-monospace,Menlo,Consolas,monospace}}
.s{{font-size:11px;padding:2px 8px;border-radius:20px;text-transform:uppercase;letter-spacing:.04em}}
.s.done{{background:#2e9e5b22;color:#2e9e5b}} .s.doing{{background:#2f6fd022;color:#2f6fd0}}
.s.blocked{{background:#c8452f22;color:#c8452f}} .s.review{{background:#c9942a22;color:#c9942a}}
.s.todo{{background:var(--line);color:var(--dim)}}
ul{{margin:0;padding-left:18px}} li{{margin:4px 0}}
.foot{{margin-top:36px;color:var(--dim);font-size:12.5px}}
</style>
<div class=wrap>
<h1>{PROJECT}</h1>
<div class=dim>{counts["done"]} of {len(tasks)} done &middot; generated {esc(now())}
&middot; {esc(", ".join(people))}</div>
<div class=bar>{bars}</div>
<div class=dim>{" &middot; ".join(f"{s} {counts[s]}" for s in STATUSES)}</div>

<h2>Cross-person dependencies</h2>
<ul>{crossing}</ul>

<h2>All tasks</h2>
<table><tr><th>ID</th><th>Title</th><th>Owner</th><th>M</th><th>Status</th>
<th>Waiting on</th><th>Last update</th></tr>{"".join(rows)}</table>

<div class=foot>Generated by <code>tools/track.py render</code> from
<code>tracker/tasks/</code>. Do not edit this file; edit the tasks.</div>
</div>"""
    out = BUILD / "index.html"
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  ({len(tasks)} tasks)")


# --------------------------------------------------------------------- entry


def main():
    p = argparse.ArgumentParser(
        prog="track",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--as", dest="as_", metavar="NAME", help="act as this person")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *args, **kw):
        s = sub.add_parser(name, **kw)
        s.set_defaults(fn=fn)
        for a_, k_ in args:
            s.add_argument(*a_, **k_)
        return s

    add("status", cmd_status)
    add("phase", cmd_phase)
    add("docs", cmd_docs)
    add("next", cmd_next, (("--for",), dict(dest="for_", metavar="NAME")))
    add("blocked", cmd_blocked)
    add("mine", cmd_mine, (("--for",), dict(dest="for_", metavar="NAME")))
    add("show", cmd_show, (("id",), {}))
    add("start", cmd_start, (("id",), {}))
    add("review", cmd_review, (("id",), {}))
    add("done", cmd_done, (("id",), {}))
    add(
        "block",
        cmd_block,
        (("id",), {}),
        (("--on",), dict(default="")),
        (("why",), dict(nargs="?", default="")),
    )
    add("unblock", cmd_unblock, (("id",), {}), (("note",), dict(nargs="?", default="")))
    add("log", cmd_log, (("id",), {}), (("message",), {}))
    add("comment", cmd_comment, (("id",), {}), (("message",), {}))
    add("assign", cmd_assign, (("id",), {}), (("to",), {}))
    add(
        "add",
        cmd_add,
        (("id",), {}),
        (("--title",), dict(required=True)),
        (("--owner",), dict(default="")),
        (("--area",), dict(default="")),
        (("--milestone",), dict(default="")),
        (("--depends",), dict(default="")),
        (("--bench",), dict(default="")),
    )
    add("render", cmd_render)
    add(
        "check",
        cmd_check,
        (("--max-idle-days",), dict(type=int, default=7)),
        (("--max-in-flight",), dict(type=int, default=3)),
    )

    a = p.parse_args()
    sys.exit(a.fn(a) or 0)


if __name__ == "__main__":
    main()
