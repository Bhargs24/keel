# spec/ - the source of truth

*Class: **LIVING** · Last-updated: · Owner: <who>. This folder is **what** the product is and **why**. The build is measured against it; when code and spec disagree, the spec is what a task is audited against.*

The pipeline fills this folder in order. Nothing here is written by hand in a hurry - each document is produced by its specialist to the bar in `docs/00-RULES/DOC-RULEBOOK.md` (source-or-silence, differentiate-or-don't, complete-not-stub, bottom-up numbers).

## The map

| Folder | What lives here | Written by | Phase |
|---|---|---|---|
| `00-START-HERE/` | this map, and the **doc register** below | you | - |
| `01-Company/` | the canonical narrative, vision/mission/values, one-pager, positioning | business-analyst | Discover |
| `02-Product/` | the master **PRD**, the per-module specs (`prd/`), user stories, success metrics, flows | product-manager | Define |
| `03-Technical/` | technical design, tech stack, data model, tools & accounts, the **build roadmap** | tech-architect | Architect |
| `06-Design/` | the design brief, the design system (tokens + components), screen mockups | design-lead | Design |
| `04-Business/` | market analysis, competitor analysis, GTM, business model, unit economics | market-researcher + business-analyst | Discover |
| `05-Finance/` | cost-to-run, financial model, the fundraise ask | business-analyst | Discover |

Each document inherits from the one before it: the product serves the business's wedge; the architecture serves the product's requirements; the build roadmap sequences the architecture. A change upstream that isn't threaded downstream is a contradiction, and `/feasibility` will find it.

## The doc register - the tracker for the front half

Keep this current. It is how `/status` knows which phase the project is in, and how a gap in the document set stays visible. Mark each **☐ not started · ◐ in progress · ☑ done**, dated.

| Doc | Purpose | Status |
|---|---|---|
| `01-Company/COMPANY-NARRATIVE.md` | the one canonical story every doc inherits | ☐ |
| `01-Company/POSITIONING.md` | category, "we are / are not", the wedge | ☐ |
| `01-Company/ONE-PAGER.md` | the two-minute exec summary | ☐ |
| `04-Business/MARKET-ANALYSIS.md` | TAM/SAM/SOM bottom-up, the beachhead, why now | ☐ |
| `04-Business/COMPETITOR-ANALYSIS.md` | the field, the 2×2, why we win | ☐ |
| `04-Business/BUSINESS-MODEL.md` | pricing, the value metric, the tiers | ☐ |
| `04-Business/UNIT-ECONOMICS.md` | one customer, fully costed | ☐ |
| `04-Business/GTM.md` | the first ten and the first thousand customers | ☐ |
| `05-Finance/COST-TO-RUN.md` | the real monthly run cost at a stated scale | ☐ |
| `02-Product/PRD.md` | the master PRD | ☐ |
| `02-Product/prd/M*.md` | the module specs, at requirements depth | ☐ |
| `02-Product/USER-STORIES.md` | stories + acceptance criteria per persona | ☐ |
| `02-Product/SUCCESS-METRICS.md` | the north-star and the metrics under it | ☐ |
| `02-Product/FLOWS.md` | the critical journeys, incl. the unhappy paths | ☐ |
| `06-Design/DESIGN-BRIEF.md` | the art direction: thesis, palette, type, layout | ☐ |
| `06-Design/DESIGN-SYSTEM.md` | the tokens and component inventory | ☐ |
| `06-Design/mockups/*.html` | real screen mockups covering every state | ☐ |
| `03-Technical/TECHNICAL-DESIGN.md` | the system, its boundaries, its failure posture | ☐ |
| `03-Technical/TECH-STACK.md` | every choice, justified | ☐ |
| `03-Technical/DATA-MODEL.md` | entities, tenancy columns, the event catalogue | ☐ |
| `03-Technical/TOOLS-AND-ACCOUNTS.md` | everything to set up or buy | ☐ |
| `03-Technical/BUILD-ROADMAP.md` | the dependency-ordered plan `/plan` loads | ☐ |

*Add rows as the product grows. A row that stays ☐ while the build moves past it is a gap the next audit will catch.*
