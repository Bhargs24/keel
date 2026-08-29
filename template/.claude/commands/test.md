---
description: Run the tests, read the failures, and say what is actually broken - with QA judgement, not just a pass/fail count.
argument-hint: [optional path or test name to focus on]
---

**Run the suite and tell the truth about it.** Not "12 failed" - *what* failed,
*why*, and whether it's the code, the test, or the fixture.

## Run it

```
make test
```

(or the focused runner for `$ARGUMENTS`). If `make test` isn't wired for the
languages present yet, run the actual test command for each and say which.

## Read the failures, don't just count them

For each failure: the assertion that failed, the value it got versus expected,
and the likely cause. Distinguish:
- **A real defect** - the code is wrong. Say what's wrong and where.
- **A wrong test** - the test encodes the wrong expectation. Say so; fixing the
  code to match a wrong test is worse than the bug.
- **A flaky test** - passes and fails without a code change. It's a defect:
  quarantine it and note it, don't re-run until it's green.

## Then check coverage of the risk, not the line count

Use the **qa** subagent when a change needs test coverage, or when you're not
sure the suite actually protects the thing most likely to break. It writes tests
at the right level and confirms they fail before the change. A green suite that
doesn't cover the dangerous path is not a passing grade.

## Report

The count, then the substance: what's actually broken and what it means, what you
fixed or added, and - if green - what the suite genuinely proves and what it
doesn't. Never report "all passing" as if that settles it; say what "all" covers.
