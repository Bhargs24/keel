---
description: Load the project, the rules, and exactly where the work stands
---

You are starting a session on the project. **Do all of this yourself, without asking.**
Read first, run the tools, then give one short briefing. Do not begin any code.

## 1 · Load the rules and the context

Read, in this order:

1. `docs/00-RULES/THE-RULEBOOK.md` — the one book. Everything else is depth on it.
2. `docs/20-WORK/INTEGRATION.md` — what is being built, who owns what, where the two halves join, how split work merges.
3. `CLAUDE.md` — the hard invariants and the routing table.
4. Whatever plan lives in `docs/20-WORK/`, for the person who is here.
5. The two most recent files in `docs/40-HANDOFF/`, if any exist. **These carry what the last session knew and did not write down anywhere else.**
6. `docs/10-STATUS/NOW.md` — what is claimed, and by whom.

If `docs/` and your specification is empty, run `your spec-fetch step, if you have one` before reading any specification.

## 2 · Get the real state, by running the tools

Never report state from memory or from a document. Run:

```
python tools/track.py status
python tools/track.py mine
python tools/track.py next
python tools/track.py blocked
git rev-parse --abbrev-ref HEAD
git log --oneline -5
git status --porcelain
```

## 3 · Brief them, in under twenty lines

Cover exactly this, and nothing else:

- **Where the project is.** Done versus total, and which milestone that means.
- **What the last session did**, from the handoff and the recent commits. If there is no handoff and no history, say so plainly: this is the first session.
- **What is in flight**, and whether anything has gone quiet.
- **What is ready for this person now**, dependencies satisfied, with your recommendation for which one and why in a sentence.
- **What they are waiting on from the other person**, and what the other person is waiting on from them.
- **Anything wrong that needs saying**: on `main`, a branch with no owner prefix, uncommitted changes, an empty `docs/` and your specification, or a task that has been in flight with no update.

## 4 · Then stop

**Propose the next task and wait.** Do not start work, do not create a branch, do not edit anything until they say what they want.

When they do say, run the whole ceremony yourself: claim it in `NOW.md`, `track start`, create the branch, read the step's spec. **Never ask them to run a command you can run.**
