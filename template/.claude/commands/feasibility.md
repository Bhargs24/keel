---
description: Phase 4 - the gate. Spawn the auditor to check the business, product, and technical plans together and return GO / REVISE / NO-GO.
argument-hint: [none]
---

**Phase 4 · Feasibility - can development actually start?**

This is the gate that decides whether the build begins. It runs on the three
plans together, because the failure that kills projects is the seam between them.

**Gate check first.** All three must exist: the business case (`spec/01-Company`,
`spec/04-Business`, `spec/05-Finance`), the product (`spec/02-Product/PRD.md`),
and the technical plan (`spec/03-Technical/BUILD-ROADMAP.md`). If any is missing,
name it and run the phase that produces it.

## Spawn the auditor

Use the **feasibility-auditor** subagent. It writes a dated **SNAPSHOT** to
`docs/50-AUDITS/<date>-feasibility.md` and checks:

- **Each plan alone** - the business (sized bottom-up? wedge structural? economics
  positive? run cost affordable?), the product (every core job a complete flow?
  states and edges specified?), the technical plan (build order sound, parsed and
  proven free of order violations? stack justified? tenancy explicit?).
- **The three together** - does the product deliver the business's wedge or has it
  drifted? Does the architecture serve *this* product? Do the developer-weeks fit
  a realistic team? Does the run cost fit inside the unit economics? What single
  point of failure carries the whole plan?

It separates what it checked **mechanically** (a real result) from what it
checked by **judgement** (not a proof of absence), and it never passes something
it could not verify - that becomes `CANNOT VERIFY`.

## The verdict, then the next action

Report the auditor's verdict verbatim and act on it:

- **GO** → the plans hold. Propose `/plan` to load the build roadmap into the
  tracker, then the build begins.
- **REVISE** → list each gap, its severity, and which document fixes it. Route
  back to the owning phase (`/discover`, `/define`, or `/architect`), fix it, and
  re-run `/feasibility`. Do not start building on a REVISE.
- **NO-GO** → say so plainly and say what would have to change. The honest next
  action is to rethink, not to build.

**Do not soften the verdict.** A false GO costs far more than an honest REVISE.
