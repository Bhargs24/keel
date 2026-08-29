---
description: Phase 3 — the technical plan. Spawn the architect to design the system and produce the dependency-ordered build roadmap.
argument-hint: [optional focus, e.g. "just the data model"]
---

**Phase 3 · Architect — is it buildable, in what order, with the tools we have?**

$ARGUMENTS

**Gate check first.** The PRD must exist (`spec/02-Product/PRD.md`). If it
doesn't, stop and run `/define`.

## Spawn the architect

Use the **tech-architect** subagent to produce, into `spec/03-Technical/`:
- `TECHNICAL-DESIGN.md` — the components, how they communicate, the trust
  boundaries, and the failure posture (what happens when each dependency is down).
- `TECH-STACK.md` — every choice justified against the alternative it beat and
  tied to a requirement. Prefer boring and proven unless a requirement forbids it.
- `DATA-MODEL.md` — the entities and relationships, with an **explicit owner /
  tenant column on every user-owned table** (this is what `/secure` proves), and
  the event catalogue if event-sourced.
- `TOOLS-AND-ACCOUNTS.md` — everything to set up or buy, with an estimated cost.
- `BUILD-ROADMAP.md` — the heart: every work item as a row with a stable **ID**,
  a **milestone** (a demoable gate), a **workstream** (parallel track), its
  **dependencies**, its **size** in developer-weeks, and what it **delivers**
  (traced to a PRD module). Grouped by milestone, with the critical path and
  per-milestone exit criteria.

## Verify the order, then record and gate

- The architect must verify mechanically that **no build step depends on a later
  one**. Confirm that check ran.
- Note every paid choice's run cost so `spec/05-Finance/COST-TO-RUN.md` is real.
- Update the doc register.
- Give the developer a **one-screen summary**: the stack in a line, the milestone
  spine, the total developer-weeks, and the riskiest technical assumption.
- **The gate:** propose `/feasibility` next — the build does not start on three
  plans that have never been checked against each other. Wait for the yes.
