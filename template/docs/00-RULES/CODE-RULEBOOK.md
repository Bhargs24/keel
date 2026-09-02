# The Code Rulebook

*Class: **LIVING** · Last-updated: · Owner: <who>. The laws for the code itself. Every coding session, human or AI, opens against this. If a rule here is wrong, change it here first; never quietly break it. Fill the language-specific parts once `/architect` has chosen the stack.*

---

## 0 · The six prime directives

1. **Never assume. Never invent.** If the spec does not say it, you do not know it. Find it in `spec/`, or stop and ask. A plausible guess written confidently is the most expensive thing you can produce.
2. **Every error is caught, typed, logged, and handled.** No silent failure. No bare catch. No swallowed exception. Ever. (§2)
3. **Everything is testable, and everything is tested.** If you cannot test it, the design is wrong. (`TESTING-STANDARD.md`)
4. **Every change declares its blast radius** before it is made: what reads this, writes this, documents this, tests this. (`CHANGE-PROTOCOL.md`)
5. **Every change is logged.** Code changelog, doc changelog, or both. An unlogged change did not happen.
6. **Production-grade or not at all.** Complete on the first pass: real data paths, every state, every error, every edge case in the spec. No mocks, stubs, TODOs, demos, or happy-path-only. If it cannot be built completely, stop and say so. (`DELIVERY-PROTOCOL.md`)

---

## 1 · Structure and modularity

### 1.1 The dependency rule (enforced in CI by `tools/dep_check.py`, not by goodwill)

Modules may only depend **inward**. `/scaffold` writes your real layout and edges into `tools/boundaries.json`; the check fails the build on a violation. An example shape (yours will differ):

```
apps/*          may import  packages/*
services/*      may import  packages/*
packages/*      may import  packages/* (lower layers only)
packages/shared may import  NOTHING internal
```

- **No circular dependencies.** The check fails the build.
- **No app imports another app.** No service reaches into another service's internals; they talk over a contract.
- **Generated code is never hand-edited.** If it is wrong, its source is wrong: fix the source, regenerate, commit the result.

### 1.2 Module boundaries

Every module has:
- **One index file that is its entire public surface.** Everything else is internal. A caller reaching past the index is a defect.
- **A short README** stating what it owns, what it depends on, and what it deliberately does not do.
- **Its own tests, colocated.**

**A module you cannot describe in one sentence is two modules.**

### 1.3 Size limits (guidance, but a breach needs a reason in the PR)

| Unit | Limit | Why past it is a smell |
|---|---|---|
| Function | ~50 lines | it is doing two things |
| File | ~400 lines | it is two modules |
| Function arguments | ~4 | the shape wants an object |
| Nesting depth | ~3 | invert with early returns |

These are not laws; they are alarms. When one trips, the fix is usually to extract, not to argue for the exception.

---

## 2 · Errors are typed, coded, and never silent

> **No bare `except`. No ignored error return. No swallowed promise rejection. No empty catch.** Every failure is caught, typed, given a stable code, logged with context, and handled or propagated deliberately.

- **A stable error code** so a failure is greppable and a support question is answerable. Use a **prefix taxonomy**, or the codes are not codes:

| Prefix | For | Example |
|---|---|---|
| `VAL_` | input failed validation | `VAL_EMAIL_MALFORMED` |
| `AUTH_` | authentication or authorization | `AUTH_FORBIDDEN` |
| `NOTFOUND_` | a resource does not exist | `NOTFOUND_ORDER` |
| `CONFLICT_` | a state or uniqueness conflict | `CONFLICT_DUPLICATE_KEY` |
| `DEP_` | a downstream dependency failed | `DEP_STRIPE_TIMEOUT` |
| `INTERNAL_` | our own bug, should never happen | `INTERNAL_INVARIANT_BROKEN` |

- **Fail safe.** On low confidence or ambiguity, do the safe thing and surface it. **Never fabricate a value to keep going. Never invent a number.**
- **The unhappy paths are the feature.** A timeout, a partial write, a retry, a dependency down: each has defined behaviour, not an unhandled throw.
- **When something breaks, follow `DEBUGGING-PROTOCOL.md`:** root cause before fix, reproduce before you believe it, read the real error, one cause one fix.

---

## 3 · Reusability, and not repeating yourself

The classic failure of AI-written code is **sprawl**: the same logic pasted five times with small variations, so a fix has to be made five times and one is always missed. Guard against it deliberately.

- **The rule of three.** The first time, write it. The second time, notice. The third time, extract it into one named, tested place. Do not abstract on the first sight (premature abstraction is its own sprawl), but do not paste a third time.
- **One source of truth per fact.** A validation rule, a constant, a piece of business logic lives in exactly one place. If two files both know that an order over $10,000 needs approval, one of them is a bug waiting to happen.
- **Before writing a helper, search for it.** The AI's instinct is to write a new `formatDate` every file. Look first; reuse what exists; put a genuinely new shared thing where the whole module can find it.
- **Name the seam, don't copy across it.** When two features need the same thing, extract the shared thing and depend on it; do not fork it.
- **Delete on sight.** Dead code, a commented-out block, an unused export, a "v2" left beside "v1". Unused code is not free; it is a lie about what the system does.

---

## 4 · Logging, observability, and privacy

- **Structured logs** with a `trace_id` that follows a request across boundaries, so a failure can be reconstructed after the fact rather than reproduced live.
- **Log the decision, not the diary.** A log line answers "why did it do that", not "it did step 4".
- **No personal data in logs, ever.** Not a name, email, phone, message body, or raw user content. Ids, lengths, hashes, confidences only. Hard invariant, checked in review.
- **Health and failure are both visible.** There is a way to see the system is healthy (a check, basic metrics) and a way to see it broke (error tracking). Code you cannot observe in production is code you cannot debug in production.

---

## 5 · Secrets

No credential, key, or token in the repo, in client-side code, or in a log. The secret scan (`tools/`) catches the obvious ones on every write and in CI; **you** catch the config committed by habit and the key bundled into the client. Secrets come from a manager and are injected at runtime.

---

## 6 · Naming and shape

- **Names say what a thing is, not how it is built.** A function is named for its effect; a variable for its meaning. A person manages *notifications*, not *webhook configs*.
- **Match the surrounding code.** A file reads like the code around it: the same idioms, comment density, and error style. Consistency beats personal preference.
- **Small, single-purpose units.** A function does one thing; a module owns one concern.

---

## 7 · When something breaks

Debugging is a discipline, not a vibe. It has its own protocol: `DEBUGGING-PROTOCOL.md`. The one-line version, because it is the rule most often broken: **find the root cause before you propose a fix, and reproduce it before you believe you found it.** A fix for a symptom you did not reproduce is a guess that will break again.

*<Language-specific sections - the formatter, the linter's ruleset, the typechecker's strictness, the test runner - go here once the stack is chosen. Keep each short: a convention nobody can recall is not one.>*

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
