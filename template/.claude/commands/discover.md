---
description: Phase 1 — the business case. Spawn the business and market specialists to produce the company, business, and finance docs.
argument-hint: [optional focus, e.g. "just the competitor analysis"]
---

**Phase 1 · Discover — is there a real, differentiated, viable business here?**

$ARGUMENTS

Read the idea in `docs/10-STATUS/NOW.md` first. Then run the two specialists.
**Spawn them; do not write these documents yourself** — they need clean context
and the research bar their briefs set.

## 1 · Market and competitors first

Use the **market-researcher** subagent to produce, into `spec/04-Business/`:
- `MARKET-ANALYSIS.md` — TAM/SAM/SOM built bottom-up (a count × a price, same
  units throughout), the beachhead segment, and the "why now" with evidence.
- `COMPETITOR-ANALYSIS.md` — the real field (each competitor sourced from their
  own site), the 2×2 on the axes that matter here, and — per serious competitor —
  the structural reason they can't copy the wedge.

The market-researcher gives the business-analyst ground truth to build on, so it
goes first.

## 2 · Then the business case

Use the **business-analyst** subagent to produce, drawing on the market work:
- `spec/01-Company/COMPANY-NARRATIVE.md` — the one canonical story (problem →
  insight → what we build → why now → why us). Everything downstream inherits it.
- `spec/01-Company/POSITIONING.md` and `ONE-PAGER.md`.
- `spec/04-Business/BUSINESS-MODEL.md`, `UNIT-ECONOMICS.md`, `GTM.md`.
- `spec/05-Finance/COST-TO-RUN.md` — the real monthly run cost at a stated scale,
  per named vendor and rate (the feasibility gate needs this).

## 3 · Record and gate

When both are done:
- Copy the narrative's core into `CLAUDE.md`'s "What we are building" section.
- Update the doc register in `spec/00-START-HERE/` (create it if absent): mark
  each doc done, dated.
- Give the developer a **one-screen summary**: the wedge in a sentence, the
  market in a number, the unit economics in a line, and the single biggest risk
  to the business case.
- **The gate:** if the specialists concluded there is *not* a real, differentiated,
  viable business, say so plainly and stop — the next action is to rethink the
  idea, not to write a product spec for a business that isn't there. Otherwise,
  propose `/define` and wait for the yes.
