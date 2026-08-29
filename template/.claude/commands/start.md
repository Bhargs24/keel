---
description: Open a session — load the rules, detect the pipeline phase, read the real state, and brief in under twenty lines. Starts nothing.
---

You are starting a session. **Do all of this yourself, without asking.** Read
first, run the tools, then give one short briefing. Do not begin any work.

## 1 · Load the rules and the context

Read, in this order:

1. `docs/00-RULES/THE-RULEBOOK.md` — the one book. Everything else is depth on it.
2. `CLAUDE.md` — what we're building and the hard invariants.
3. The two most recent files in `docs/40-HANDOFF/`, if any exist. **These carry
   what the last session knew and did not write down anywhere else.**
4. `docs/10-STATUS/NOW.md` — the idea, what's claimed, and by whom.

## 2 · Detect the phase

This project moves through a pipeline. Work out where it is from what exists on
disk (the table in `/status` has the full logic), because the next action
depends on it:

- No business docs yet → the next move is `/discover`.
- Business but no PRD → `/define`. PRD but no build roadmap → `/architect`.
- Roadmap but no feasibility audit → `/feasibility`. Audit but no tasks → `/plan`.
- Tasks in the tracker → we're **building**; read the real build state below.

## 3 · Get the real state, by running the tools

Never report state from memory. Run:

```
python tools/track.py status
python tools/track.py mine
python tools/track.py next
python tools/track.py blocked
git rev-parse --abbrev-ref HEAD
git log --oneline -5
git status --porcelain
```

## 4 · Brief them, in under twenty lines

- **The phase**, and the single next action it implies.
- **What the last session did**, from the handoff and the recent commits. If there
  is no handoff and no history, say so plainly: this is the first session.
- **The document set** — which pipeline docs exist and which don't, so a gap in
  the front half is visible before it bites the build.
- **If building:** what's ready now, dependencies satisfied, with your
  recommendation for which one and why in a sentence; what's in flight and whether
  it's gone quiet; what each person is waiting on from the other.
- **Anything wrong:** on `main`, a branch with no owner prefix, uncommitted
  changes, a stale feasibility audit, a task in flight with no update.

## 5 · Then stop

**Propose the next action and wait.** Do not start work, create a branch, spawn a
specialist, or edit anything until they say what they want. When they do, run the
whole ceremony yourself — **never ask them to run a command you can run.**
