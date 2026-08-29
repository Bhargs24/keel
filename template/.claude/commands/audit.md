---
description: Verify that work marked done is genuinely done, against its definition of done
argument-hint: [TASK-ID | milestone e.g. M0 | person | "all"]
---

Audit: **$ARGUMENTS**

`track done` is self-declared and nothing verifies it. **This does.** The build
plan gives every step a `Test / DoD`, so there is an objective standard to check
against rather than an opinion.

## Scope

- A **TASK-ID** → audit that one, in depth.
- A **milestone** (`M0`) → every `done` task in it.
- A **person** (any key from `tracker/people.toml`) → every `done` task of theirs.
- **`all`** → every `done` task. Say up front how many, and work through them.

```
python tools/track.py status
grep -l '^status: done' tracker/tasks/*.md
```

## For each task, check five things

Read the step's block in `your build plan or issue tracker` first. Its
`Delivers`, `Test / DoD`, `Module`, `Events / API` and `Debug notes` are the
standard. Then:

**1 · Does the code exist, where the step said it would?**
The `Module` field names the file or boundary. If nothing is there, the task is
not done, whatever the tracker says.

**2 · Does it meet the stated definition of done?**
Go through `Test / DoD` clause by clause. **Quote the clause, then say whether it
holds and how you know.** "Looks fine" is not an answer.

**3 · Do the tests exist and do they test the risk?**
Not "are there tests" but "is the thing most likely to break covered". For
ledger work: idempotency and replay determinism. For a screen: every state in
the spec. For the deterministic engine: a valid method it did not expect.

**4 · Were the debug and error notes honoured?**
The step's `Debug + change notes` name the log points, the edge cases and the
flag. Silent failure is a defect, not a style choice.

**5 · Is the paperwork true?**
Changelog written, any contradicted document updated, `NOW.md` accurate, and the
task's log actually reflecting what happened.

## Verdict per task, and be strict

| | |
|---|---|
| **DONE** | every DoD clause holds, tests cover the risk, paperwork true |
| **DONE WITH GAPS** | works, but something named is missing. **List each gap** |
| **NOT DONE** | a DoD clause does not hold, or the code is not there |
| **CANNOT VERIFY** | you could not check it. **Say why.** Never pass something you did not check |

## Then act on it

For anything **NOT DONE**:

```
python tools/track.py block <ID> --on "" "audit: <the clause that fails>"
python tools/track.py log <ID> "audit <date>: <what is missing>"
```

For **DONE WITH GAPS**: log the gaps on the task so they are not lost, and say
whether they are worth a follow-up task now or a note for later.

## Report

A table of every task audited with its verdict, then the detail only for
anything that is not clean. Finish with **one honest paragraph on whether the
progress number can be trusted.**

**A clean audit that finds nothing is a real result, and so is a bad one. Do not
soften a verdict to be encouraging.**
