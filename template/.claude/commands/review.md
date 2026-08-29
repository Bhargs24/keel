---
description: Review this branch against the rulebook and the spec before pushing
---

Review the current branch **before it is pushed**. You are looking for what a
grep cannot find. `make check` already ran the mechanical gates; do not repeat them.

```
git diff --stat main...HEAD
git diff main...HEAD
python tools/track.py show <the TASK-ID in the branch name>
```

Read the step's block in `your build plan or issue tracker` and whatever its
`Spec:` field points at. **You are reviewing against that, not against taste.**

## What to look for, in this order

**1 · Does it do what the step said it would?** Compare against `Delivers` and
`Test / DoD`. A step that builds something adjacent but not the thing is the
most common and most expensive failure here.

**2 · Spec drift.** Does the behaviour match the surface spec, including the
states? Loading, empty, below-confidence, error, offline, thin-data are part of
the screen, not extras. **A missing state is a missing feature.**

**3 · The invariants** (`CLAUDE.md`). Especially: no MCQ in the daily loop, no
student self-signup, consent gating every child-data read and write, a model
never deciding a calculation, corrections as new events rather than edits.

**4 · Error handling.** Every failure typed, coded, logged, handled. **No silent
catch, no bare `except`, no ignored error return.** What happens on a timeout, a
retry, a partial write?

**5 · PII.** No student name, phone, answer text or raw audio in a log line.
Ids, lengths, hashes, confidences only.

**6 · Tests that are actually about the risk.** Does a test exist for the thing
most likely to break, or only for the happy path? For anything touching the
ledger: idempotency and replay determinism.

**7 · Things left behind.** Debug prints, commented-out code, a config value
that only works on this machine, a dependency added without a reason.

**8 · Blast radius.** What else reads, writes, documents or tests this? Was any
of it updated in the same change?

## Report

Group findings as **must fix before push**, **should fix**, and **worth knowing**.
For each: the file and line, what is wrong, and **the concrete failure it causes**.

**If you find nothing, say so plainly and say what you checked.** A review that
always finds something is as useless as one that never does.
