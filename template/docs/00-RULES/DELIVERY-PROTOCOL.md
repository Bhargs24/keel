# The Delivery Protocol

*Class: **LIVING** · Last-updated: · Owner: <who>. How work is scoped, run, recorded and finished. Depth on `THE-RULEBOOK.md` Part 3.*

---

## 1 · Production-grade or not at all

**The single most expensive default in agentic coding: asked for a feature, the agent builds a demo.** A mock, a happy path, a `TODO: handle errors`, a hardcoded array where a query belongs. It runs, it demos, and it is not the thing.

### The rule

> **Every feature is built production-grade, complete, on the first pass. Never a mock, never a stub, never a demo, never a happy path, never "we'll wire it up later".**

If a feature cannot be built completely, **say so and stop.** Do not build a fraction of it and present it as done.

### What "complete" means, concretely

A feature is not complete until every one of these is true.

- [ ] **The real data path.** Real queries, real events, real state. No hardcoded arrays, no fixture masquerading as a source, no `if (DEBUG)` branch carrying the logic.
- [ ] **Every state rendered.** Loading, empty, error, offline, partial, and every state the spec names for that screen. **The empty and error states are part of the feature, not polish.**
- [ ] **Every error path handled**, typed and coded per `CODE-RULEBOOK.md`. Including the ones that are annoying to trigger.
- [ ] **Every edge case in the spec.** The spec lists them. Implement them, do not defer them.
- [ ] **Validation at the boundary**, on real and hostile input.
- [ ] **Authorization enforced** server-side, in middleware, not in the component. Provable with `/secure`.
- [ ] **Structured logs and metrics** on the paths it adds. No PII.
- [ ] **Tests at every level the change touches**, per `TESTING-STANDARD.md`.
- [ ] **Docs and changelog** updated in the same change.

### Banned in a pull request

`TODO`, `FIXME`, `for now`, `temporary`, `mock`, `stub`, `placeholder`, `dummy`, `hardcoded`, `we'll fix later`, `not implemented`, commented-out code.

**`tools/no_placeholders.py` greps for these in CI and fails the build.** A genuine deferral is a **new work item with an ID**, referenced in the code by that ID — not a comment nobody will ever find.

### The one legitimate exception

A **deliberate, named, scheduled** deferral: a work item ID, a reason, an owner, a milestone. `WORK-ITEM: W1.8 backfill engine, deferred to M2` is legitimate. `// TODO: handle the error case` is not.

---

## 2 · Sprints

Sprints exist so work has a boundary, a deliverable, and a moment where somebody checks. Without them, agentic building becomes an infinite stream with no gate.

- **A sprint is a set of tracker tasks with a single demoable deliverable**, drawn from one milestone in the build roadmap. Record it in `docs/20-WORK/sprints/`.
- **It ends with a demo and an audit**, not a feeling of being done. Run `/audit` on the sprint's tasks; the deliverable is real only if their definitions of done hold.
- **A wrong direction is caught at the sprint boundary, not a month later.** That is the whole reason the boundary exists.

---

## 3 · The log taxonomy

The tracker log is the shared memory. Keep it useful by keeping it typed. Each entry is one of:

| Type | For | Example |
|---|---|---|
| **decision** | a choice made, and why | "chose Postgres advisory locks over Redis — one fewer dependency" |
| **surprise** | reality differed from the spec or the plan | "the vendor's webhook is at-least-once, not exactly-once; added idempotency" |
| **dead end** | a path tried and abandoned, so nobody retries it | "tried the library's streaming API; it buffers the whole response, unusable here" |
| **blocked** | stuck, on what, and what would unblock it | "blocked on the event schema (W0.3); can't write the projection until it lands" |
| **state** | where it's being left, at session end | "half-done: read path works, write path stubbed at handlers/orders.go:88" |

**A diary of what you did is noise. The five above are signal** — they are the things the next person (often you, three days later) would otherwise have to rediscover.

---

## 4 · Finishing

A task is finished when `/wrap` has run: the honest state is logged, the task is moved (`review`/`done`/`block`), the handoff is written with its *what-I-know-that-isn't-written* section, every changed file is changelogged, any contradicted document is fixed in the same change, and `make check` is green. **Not before.**

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
