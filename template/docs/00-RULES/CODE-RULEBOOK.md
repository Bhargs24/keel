# The Code Rulebook

*Class: **LIVING** · Last-updated: · Owner: <who>. The laws for the code itself. Depth on `THE-RULEBOOK.md`. Fill the language-specific parts once `/architect` has chosen the stack.*

---

## 1 · Module boundaries

A codebase without enforced boundaries rots into a monolith one convenient import at a time. `tools/dep_check.py` enforces the boundary in CI; this is the rule it enforces.

- **Layers only import downward.** Applications and services may import shared packages; shared packages import only lower shared packages; the generated shared package imports nothing internal.
- **No app imports another app. No service reaches into another service's internals** — they talk over a contract, not by importing each other's guts.
- **No circular dependencies.** A cycle is a design smell the check treats as an error.

Set your module prefix and the allowed edges in `tools/dep_check.py`. **The split has to be visible in the directory tree**, because that is the only way it can be checked.

---

## 2 · Errors are typed, coded, and never silent

> **No bare `except`. No ignored error return. No swallowed promise rejection. No empty catch.** Every failure is caught, typed, given a stable code, logged with context, and handled or propagated deliberately.

- **A stable error code** (e.g. `VAL_SCHEMA_INVALID`, `AUTH_FORBIDDEN`) so a failure is greppable and a support question is answerable.
- **Fail safe.** On low confidence or ambiguity, do the safe thing and surface it — never fabricate a value to keep going. **Never invent a number.**
- **The unhappy paths are the feature.** A timeout, a partial write, a retry, a dependency down — each has defined behaviour, not an unhandled throw.

---

## 3 · Logging and privacy

- **Structured logs** with a `trace_id` that follows a request across services.
- **No personal data in logs, ever.** Not a name, an email, a phone, a message body, raw user content. Ids, lengths, hashes, and confidences only. This is a hard invariant, checked in review.
- **Log the decision, not the diary.** A log line should answer "why did it do that", not narrate every step.

---

## 4 · Generated code is never hand-edited

If a file is generated from a source (a schema, an OpenAPI spec, an event catalogue), **nobody edits the output, ever.** If it's wrong, the source is wrong: fix the source, regenerate, commit the result. CI fails on a hand-edited generated file and, separately, on generated output that has drifted from its source. `make gen` regenerates.

---

## 5 · Naming and shape

- **Names say what a thing is, not how it's built.** A function is named for its effect; a variable for its meaning.
- **Match the surrounding code.** A file reads like the code around it — the same idioms, the same comment density, the same error style. Consistency beats personal preference.
- **Small, single-purpose units.** A function does one thing; a module owns one concern. If you can't name it in a short phrase, it's doing too much.

---

## 6 · Secrets

No credential, key, or token in the repo, in client-side code, or in a log. `tools/` runs a secret scan on every write and in CI, but the scan catches the obvious ones — **you** catch the config committed by habit and the key bundled into the client. Secrets come from a manager and are injected at runtime.

*<Language-specific sections — formatting, linting, the typechecker's strictness, the test runner — go here once the stack is chosen. Keep each short: a convention nobody can recall is not one.>*

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
