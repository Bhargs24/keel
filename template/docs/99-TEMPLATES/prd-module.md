# <Module ID> · <Module name>

*Class: **LIVING** · Last-updated: · Part of `spec/02-Product/PRD.md`. Requirements depth: a builder can implement this without asking a question.*

## What it is
<Two or three sentences. What this module does and the user need it serves. Traces to a user story and a business goal.>

## User stories it satisfies
- As a <persona>, I want <capability>, so that <outcome>. - *acceptance: <checkable criteria>*

## Screens and states
For each screen, **every state it can be in.** A missing state is a missing feature.

### <Screen name / ID>
| State | What the user sees | How it's reached |
|---|---|---|
| loading | | |
| ready | | |
| empty | | |
| partial | | |
| error | | |
| offline | | |

**Actions on this screen:**
| Action | On success | On failure |
|---|---|---|
| | | |

## Data
- **Reads:** <entities/fields, from `DATA-MODEL.md`>
- **Writes:** <entities/events>
- **Ownership:** <the tenancy column that decides who may see each row - what `/secure` proves>

## Edge cases
<The messy real-world cases, each with defined behaviour. The spec lists them so the build doesn't have to invent them.>

## Non-functional
<Performance, offline, accessibility, and any budget this module must fit.>

## Acceptance criteria
<The pass/fail checks that mean this module is done. A QA engineer writes tests from these.>
