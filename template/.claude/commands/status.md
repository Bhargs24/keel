---
description: Where the whole project stands - which pipeline phase it's in, what's done, and what the next action is.
argument-hint: [none]
---

**Give a single, honest picture of where this project is.** Do all of this
yourself by reading the files and running the tools - never from memory.

## 1 · Which phase are we in?

Run the tool - it detects the phase from what's on disk, so it's a fact, not a guess:

```
python tools/track.py phase
python tools/track.py docs
```

`phase` gives you the current step and the next command; `docs` shows the whole
document set as a checklist, so a gap in the front half is visible. For reference,
the detection is:

| If this is true | The phase is | The next action is |
|---|---|---|
| `docs/10-STATUS/NOW.md` has an idea but `spec/01-Company/` is empty | **Pre-Discover** | `/discover` |
| `spec/01-Company/` exists but `spec/02-Product/PRD.md` doesn't | **Discover done → Define** | `/define` |
| `PRD.md` exists but `spec/06-Design/DESIGN-BRIEF.md` doesn't | **Define done → Design** | `/design` (or skip to `/architect`) |
| Design exists but `spec/03-Technical/BUILD-ROADMAP.md` doesn't | **Design done → Architect** | `/architect` |
| The roadmap exists but there's no `docs/50-AUDITS/*-feasibility.md` | **Architect done → Feasibility** | `/feasibility` |
| Feasibility exists but the tracker has no tasks | **Feasibility done → Plan** | `/plan` |
| The tracker has tasks | **Building** | `/next` (or `/work`) |

## 2 · Read the real state

```
python tools/track.py status
python tools/track.py next
python tools/track.py blocked
git rev-parse --abbrev-ref HEAD
git log --oneline -5
git status --porcelain
```

Also glance at the two most recent `docs/40-HANDOFF/` files and `NOW.md`.

## 3 · Brief them, in under twenty lines

- **The phase**, and the one next action.
- **The document set:** which of the pipeline docs exist and which don't (walk
  `spec/`), so a gap in the front half is visible.
- **The build**, if building: done vs total, which milestone, what's in flight
  and whether anything has gone quiet.
- **What's ready now**, with your recommendation and one sentence of why.
- **Anything wrong:** on `main`, a branch with no owner prefix, uncommitted work,
  a feasibility audit that hasn't been re-run since the plan changed, an empty
  spec the build is about to need.

Then **stop and propose the next action.** Do not start it until they say yes.
