---
description: Phase 2 - the product. Spawn the product manager to turn the business case into a complete PRD.
argument-hint: [optional focus, e.g. "the onboarding module"]
---

**Phase 2 · Define - does the product completely solve the business problem?**

$ARGUMENTS

**Gate check first.** The company narrative and the business case must exist
(`spec/01-Company/`, `spec/04-Business/`). If they don't, stop and run `/discover`
- a product spec with no business behind it is just a feature list.

## Spawn the product manager

Use the **product-manager** subagent to produce, into `spec/02-Product/`:
- `PRD.md` (the master) - overview, personas & jobs-to-be-done, scope (in and
  explicitly out), the module map, the interfaces between modules, non-functional
  requirements, the data needed, success metrics, risks, glossary.
- `prd/M1..Mn.md` (the module suite) - one per module, at requirements depth:
  every screen and **every state** (loading, empty, partial, error, offline),
  every action and what it does on success and failure, every edge case, the data
  it reads and writes, and its own acceptance criteria.
- `USER-STORIES.md`, `SUCCESS-METRICS.md`, `FLOWS.md` (the critical journeys,
  including the unhappy paths).

For a large product, define the **module map** first, then specify the beachhead
modules fully and mark the rest as later - a complete spec of the first thing
beats a stubbed spec of everything. Say which is which.

## Record and gate

When done:
- Copy the **hard invariants** the PM identified into `CLAUDE.md` (the rules the
  build must enforce - the permission gate, the thing a model must never decide,
  any safety law).
- Update the doc register.
- Give a **short, plain recap** (2 to 4 lines, no jargon): the good news, the one thing to watch with its fix, and the single next step. The full detail is in the documents and the guide (`python tools/keel.py`) - point there, do not paste it. The recap covers: the personas, the module map, what
  the beachhead is, and the biggest gap the PM flagged.
- **The gate:** the product must completely solve the business problem for the
  beachhead. If the PM flagged a real coverage gap, the next action is to close
  it, not to move on. Otherwise, propose `/design` next - the design turns these
  screens and states into a look and feel before the architect picks the frontend
  stack. (If the product has little UI, or the visual design is already fixed,
  skip straight to `/architect` and say so.) Wait for the yes.
