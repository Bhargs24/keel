# <ID> · <title>

*Class: **LIVING**. Moves backlog → doing → review → done. This is the human-readable companion to the tracker task; the tracker holds the state, this holds the detail.*

**Spec:** `spec/02-Product/prd/<module>.md` §<section> · `spec/03-Technical/BUILD-ROADMAP.md` row `<ID>`
**Milestone:** <M0..Mn>   **Workstream:** <BE/AI/UI/...>   **Owner:** <name>   **Radius:** <T0..T3>   **Size:** <S/M/L>

## Build
<One line: what this delivers. The chunk of the spec it turns into working software.>

## Done means
- [ ] Does exactly what the spec section says, every state and edge case
- [ ] Real data path - no mocks, stubs, TODOs, or hardcoded data
- [ ] Every error typed and coded; structured logs with a trace_id; **no PII**
- [ ] Authorization enforced server-side; proved with `/secure` if it touches data
- [ ] Tests at the right level, failing before the change (`TESTING-STANDARD.md`)
- [ ] Changelog written and any contradicted doc fixed, in the same PR

## Blast radius
Reads: · Writes: · Docs: · Tests:

## Log
- YYYY-MM-DD created
