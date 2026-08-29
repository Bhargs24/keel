---
description: Pull up everything the specs say about a step, screen or topic
argument-hint: [TASK-ID, screen id, or a topic]
---

Find and summarise what the specification says about: **$ARGUMENTS**



## Where to look, in order

1. **A TASK-ID** (`BE-005`, `ST-013`, `TE-021`) → the block in
   `spec/03-Technical/BUILD-ROADMAP.md`, then whatever its `Spec:` field points at.
2. **A screen id** (`ST-11`, `PA-12`, `TE-21`) → `spec/02-Product/PRD.md` and its module specs,
   for its states, actions and backend notes.
3. **An event or projection** → `spec/03-Technical/DATA-MODEL.md`.
   **Authoritative for the wire.**
4. **A topic** → search `spec/` and `docs/` broadly, and say which documents you searched.

## Report

- **What it is**, in two or three sentences of plain language.
- **The exact requirements**: states, actions, events, definition of done.
- **What it depends on and what depends on it.**
- **The rules that bind it** — invariants from `CLAUDE.md`, and anything in the
  anti-anxiety or consent laws that applies.
- **Anything the spec does not say** that a builder would need. Say this plainly
  rather than filling the gap yourself.
- **Where you read it**, as paths, so they can go deeper.

**Quote the spec where the wording matters.** Do not paraphrase a rule into
something softer than it is.
