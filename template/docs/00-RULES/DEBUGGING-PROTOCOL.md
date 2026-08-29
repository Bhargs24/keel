# The Debugging Protocol

*Class: **LIVING** · Last-updated: · Owner: <who>. Debugging is a discipline, not a vibe. An AI's instinct is to patch the first symptom it sees; this document forbids that. Depth on `CODE-RULEBOOK.md` §7.*

> **The one rule, if you read nothing else: find the root cause before you propose a fix, and reproduce the failure before you believe you found it.** A fix for a symptom you did not reproduce is a guess that will break again, usually in front of a user.

---

## 1 · Reproduce before you fix

No fix lands without a **failing test that reproduces the defect first.** That test is the regression test: it goes red, the fix makes it green, and it stays in the suite so the bug can never return silently. If you cannot reproduce it, you do not understand it yet, and a fix is premature.

For a bug you cannot yet write a test for, reproduce it by hand and write down the exact steps before touching code. "It sometimes fails" is not a reproduction; "it fails when the input is empty and the cache is cold" is.

## 2 · Root cause, not symptom

State the **causal chain** out loud (and in the PR): "the value is null *because* the webhook is delivered at-least-once *because* the provider retries on a 500 *because* our handler times out at 3s." A fix that cannot name the cause is a guess. Reverting a symptom patch is cheaper than shipping it.

**Never treat a symptom.** Wrapping the null in `if (x)` when the real bug is that `x` should never be null hides the defect and moves it downstream, where it is harder to find.

## 3 · Read the actual error

Quote the **real** stack trace, error code, and log line. Do not infer a cause you have not observed. The single most common AI debugging failure is inventing a plausible explanation for an error it did not actually read. If the error is swallowed by a `try/except`, the first fix is to stop swallowing it, so you can see what it actually is.

## 4 · Narrow it down

Bisect the problem rather than staring at all of it:
- **Smallest input** that still fails.
- **Smallest diff** that still fails (comment things out, add them back).
- **`git bisect`** for a regression: find the exact commit that introduced it.
- **Binary-search the pipeline**: is the data wrong when it enters this function, or does this function make it wrong? Log at the boundary and halve the search each time.

## 5 · Observability is the feature, not an afterthought

You can only debug in production what you can see in production. So every new code path ships with:
- a **structured log** at a defined level, keyed by `trace_id`, that says what decision was made and why;
- a **metric** on each external-call and route boundary (latency, error rate);
- an **error** that is typed and coded (`CODE-RULEBOOK.md` §2), so the next failure is greppable.

Code you cannot observe is code you will debug by redeploying with print statements, which is the slowest loop there is. Build the visibility in the first time.

## 6 · One cause, one fix

Fix the thing you came to fix. **No "while I was in there."** An unrelated change smuggled into a bug-fix commit is how a fix introduces a new bug and nobody can tell which line did it. If you find a second bug, log it as its own work item and fix it separately.

---

## The debugging prompt (paste this)

```
Symptom: <exactly what you observed - verbatim error, no interpretation>
Expected: <what should happen, and which spec section says so>
Already ruled out: <what you have checked>

Find the ROOT CAUSE before proposing a fix. Reproduce it with a failing test
first. Read the actual error; do not guess a cause you have not observed. If you
are not sure, say so and tell me what would confirm it. One cause, one fix.
```

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
