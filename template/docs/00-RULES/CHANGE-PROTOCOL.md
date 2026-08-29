# The Change Protocol

*Class: **LIVING** · Last-updated: · Owner: <who>. How big a change is, and what that requires of you. Depth on `THE-RULEBOOK.md` Part 3 and Part 4.*

---

## The blast-radius tiers

Before editing, decide the tier. It sets how much care the change needs.

| Tier | What it is | What it requires |
|---|---|---|
| **T0** | a self-contained change: one function, one component, no shared contract touched | just do it, tested |
| **T1** | touches a module's public surface or several files within one area | trace what reads and writes it; tests at the contract level |
| **T2** | crosses a module or service boundary, or changes a shared contract | **plan mode first**; a crossing note if it enters another owner's area; contract tests both sides |
| **T3** | touches something with no undo — an append-only schema, an auth path, a money path, anything already sent to users | **plan mode, and stop-and-ask.** Prove the boundary with `/secure`. This is Part 4 of the rulebook: slow down |

**Above T0, enter plan mode before writing.** Pour the effort into the plan so the implementation is one-shot. If it goes wrong mid-implementation, re-plan — never course-correct blindly mid-stream.

---

## Trace the blast radius, always

Before any change above T0, answer four questions:

- **What reads this?** Every caller, every consumer of the output.
- **What writes this?** Every path that produces the state you're changing.
- **What documents this?** The spec, the changelog, the data model — fix the ones the change contradicts, in the same commit.
- **What tests this?** Update or add the tests that pin the new behaviour.

A change that updates the code but not the document it contradicts has created a trap. A change that updates neither the caller nor the test has shipped a bug with a clean diff.

---

## The things with no undo

Named in `THE-RULEBOOK.md` Part 4 and worth repeating, because speed everywhere else is free and here it is not:

- **An append-only schema** once real users have written to it.
- **Anything sent to a user** — an email, a message, a notification, a charge.
- **A record written into a dataset the business depends on.**
- **A public claim** in a pitch or a deck you cannot walk back.

At any of these: plan mode, ask, and prove rather than assume. A T3 change that turns out wrong is not a re-run; it is damage.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
