---
description: Close the session cleanly. Log, status, handoff, changelog, checks, commit
---

**Close this session properly. Do all of it yourself.**

## 1 · Record where the work actually stands

```
python tools/track.py show <ID>
```

`track log <ID> "..."` with the honest state it is being left in. Half-done is
fine; **half-done and silent is not.** Include anything the next session would
otherwise have to rediscover.

Then move it: `track review <ID>` if it needs eyes, `track done <ID>` if it is
finished, `track block <ID> --on <ID> "why"` if it is stuck.

**If `done` prints what it unblocks, put that in `NOW.md`** so the other person
sees it without being told.

## 2 · Write the handoff

`docs/40-HANDOFF/<YYYY-MM-DD>-<slug>.md`:

- **Done** - what actually landed
- **Half-done** - what is in flight and exactly where it stops
- **Next action** - one sentence, specific enough to start from cold
- **What I know that is not written anywhere** - the dead ends, the thing the
  spec got wrong, the reason a decision went the way it did.
  **This is the whole value of the file.**

## 3 · Leave the documents true

Changelog every file you changed. If the work contradicts a document, fix the
document in the same commit. If the specification itself is wrong, say so
plainly rather than quietly building around it.

## 4 · Check and commit

```
make check
git status --porcelain
```

Commit with a message that says what changed and **why**, not what the diff
already shows. If anything is uncommitted and should not be, say why.

**Do not push to `main`.** Push the branch and open a PR.

## 5 · One closing paragraph

What landed, what is next, and anything the developer should decide before the
next session.
