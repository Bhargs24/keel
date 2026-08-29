# Registers

*Class: **LIVING**. Four running lists that keep a project honest. Copy the ones you need into `docs/20-WORK/` (or keep the risk register inside the PRD). A register is first-class: it is where a known-unknown lives so it cannot be quietly forgotten. Every entry obeys the paired-honesty law - a risk carries its mitigation, an assumption carries how it will be checked.*

---

## Risk register

| # | Risk | Severity | Likelihood | Mitigation | How we will know it is happening |
|---|---|---|---|---|---|
| R1 | | H/M/L | H/M/L | *the fix, concretely* | *the leading indicator* |

## Assumptions register

Everything the plan rests on that is not yet proven. Grep for `ASSUMPTION:` across the specs and consolidate here.

| # | Assumption | What rests on it | How we will validate it | Status |
|---|---|---|---|---|
| A1 | | *the docs/decisions that fall if it is wrong* | *the experiment or data point* | open / validated / broken |

## Decision register (ADRs)

One row per decision that would be expensive to reverse. The full record for a big one is a **SNAPSHOT** using `decision-record.md`.

| # | Decision | Date | Why (the thing that tipped it) | What would change it |
|---|---|---|---|---|
| D1 | | YYYY-MM-DD | | *the evidence that would make this wrong* |

## Open-questions register

The things nobody has answered yet, so they do not get lost between sessions.

| # | Question | Blocks | Who decides | Status |
|---|---|---|---|---|
| Q1 | | *what cannot proceed until this is answered* | | open / answered |
