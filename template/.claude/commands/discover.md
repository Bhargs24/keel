---
description: Phase 1 - what exists, how this is better, and (for a company) the business case. Spawn the research specialists.
argument-hint: [optional focus]
---

**Phase 1 · Discover - is this genuinely better than what exists, and (if a company) is there a real business?**

$ARGUMENTS

Read the idea and the **Mode** in `docs/10-STATUS/NOW.md` first. Everything below
adapts to whether this is a **company** or a **project**. **Spawn the specialists;
do not write these documents yourself.**

## Always, in both shapes: prior art and the innovation bar

Use the **market-researcher** subagent to answer the universal question first:
**what already exists that does this or something close, and how is ours genuinely
better or more original?** It writes `spec/04-Business/PRIOR-ART.md`: the existing
things (products, open-source projects, tools, the way people do this today, each
sourced), and an honest differentiation verdict. If the honest answer is "about the
same as X", that is the finding, and by the innovation law it arrives with the fix:
the specific angle, constraint, or insight that would make this actually new and
better. **We do not proceed to build a me-too.**

## If Mode is `company`: also the business case

Have the **market-researcher** also produce `MARKET-ANALYSIS.md` (TAM/SAM/SOM
bottom-up, the beachhead, why now) and `COMPETITOR-ANALYSIS.md` (the field, the
2x2, why we win). Then the **business-analyst** produces the narrative,
positioning, one-pager, business model, unit economics (with a downside),
`GTM.md`, and `spec/05-Finance/COST-TO-RUN.md`.

## If Mode is `project` (or `experiment`): skip the money work

Do **not** produce market sizing, unit economics, GTM, or finance docs. Instead the
**business-analyst** writes a short `spec/01-Company/CONCEPT.md`: what this is, who
it is for, why it is worth building, and, front and centre, **why it is better or
newer than what already exists** (drawn from `PRIOR-ART.md`). That is the whole
front half for a project: a clear, differentiated concept. The design and the
product quality carry the rest.

## Record and gate

- Update the doc register.
- Give a **one-screen summary**: what exists, the one sentence on how this is
  better or new, and (for a company) the wedge, the market in a number, and the
  unit economics in a line, plus the single biggest risk - each with its fix.
- **The gate:** if the honest finding is that this is not meaningfully different
  from what exists and no angle makes it so, say that plainly and stop; the next
  action is a better idea, not a spec. Otherwise propose `/define` and wait.