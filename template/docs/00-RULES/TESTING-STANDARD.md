# The Testing Standard

*Class: **LIVING** · Last-updated: · Owner: <who>. "Everything is tested" needs a definition, or it means nothing. This is that definition.*

---

## 0 · Why this matters more here

**You are writing code faster than one person can read it.** Tests are not a safety net on top of review; on this team they *are* the review budget. A change is trusted because a harness proves it, not because it looked right. So the standard is stricter than the industry's, on purpose.

---

## 1 · The principle

**Test the thing most likely to break, not the thing easiest to test.** A file with 90% coverage and no test for its one dangerous path is less safe than a file with 40% coverage that pins exactly that path. Coverage is a hint; the risk is the target.

For every change, name the way it is most likely to fail, and make sure a test would catch it. If none would, write that test first.

---

## 2 · The pyramid, and what each layer owns

| Layer | Owns | Speed | Runs |
|---|---|---|---|
| **Unit** | one function, its branches and edges | milliseconds | every save |
| **Contract** | the shape between two modules or services | fast | every PR |
| **Integration** | a real path through real infrastructure (DB, cache, queue) | seconds | every PR |
| **End-to-end** | one user journey through real surfaces | minutes | every PR on critical journeys; nightly for the rest |
| **Property** | an invariant that must hold for all inputs | varies | every PR |

Don't write an end-to-end test for what a unit test proves, or a unit test for what only integration can. Put each test at the lowest level that can actually catch its failure.

---

## 3 · The rules

- **Tests fail before the change.** A test that passes without the code it claims to test is testing nothing. Where you can, show it red first — this is why the TDD discipline matters, and why writing code and test together (which shapes the test to fit the code) is banned for anything non-trivial.
- **Every spec state has a test.** For a screen, every state the spec names. For a calculation, an input the author did not anticipate. For anything append-only or money-touching, **idempotency and replay determinism**.
- **Hostile input is tested**, not just the input that confirms the happy path.
- **A flaky test is a defect.** It passes and fails without a code change. Quarantine it and fix it; never re-run until green — that's how a suite becomes decoration.
- **The bug that escaped becomes a test.** Every real defect gets a regression test that would have caught it, before the fix lands.

---

## 4 · Benches: prove a capability before wiring it in

For anything uncertain — a model's behaviour, a third-party API's real semantics, a novel algorithm — build a **bench**: an isolated harness with one variable and one number. Prove the capability on the bench, then wire it into the product. A bench is permanent; it becomes the regression suite that re-proves the capability whenever a model or a library moves. (A spike, by contrast, answers a question and is deleted.)

**No capability is wired into the product before its bench is green.**

---

## 5 · What CI runs

`make test` runs the suite, per language, only when that language changed. `make verify` runs it alongside lint and types. A red test does not land, whoever wrote it. The security proof — `trespass` on the schema — runs in `make check` and `/secure`; a `VULNERABLE` verdict is a failing test with a reproduction.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
