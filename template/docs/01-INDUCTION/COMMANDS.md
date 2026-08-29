# The commands

*Class: **LIVING** · Last-updated: · Owner: <who>. Every command, what it does, what it spawns, and when to reach for it. You do not need to memorize this — Claude reaches for these on your behalf. This is the reference for when you want to know what's happening.*

> ## If you remember three things
>
> **`/start`** when you sit down · **`/next`** to decide what's next · **`/wrap`** when you stop.

---

## The pipeline — idea to build-ready

Run in order the first time; after that, `/status` tells you which one is next.

| Command | What it does | Spawns | Gate before the next step |
|---|---|---|---|
| **`/keel "<idea>"`** | Captures the idea, clarifies only what blocks progress, starts the pipeline | — | — |
| **`/discover`** | The business case: narrative, positioning, market & competitor analysis, unit economics, cost-to-run | business-analyst · market-researcher | Is there a real, differentiated, viable business? |
| **`/define`** | The product: a master PRD, module specs, user stories, success metrics, flows | product-manager | Does it completely solve the business problem? |
| **`/architect`** | The build: architecture, tech stack, data model, tools & accounts, the dependency-ordered build roadmap | tech-architect | Is it buildable with the chosen tools? |
| **`/feasibility`** | Audits the three plans, alone and together | feasibility-auditor | **GO / REVISE / NO-GO** |
| **`/plan`** | Loads the build roadmap into the tracker as tasks with dependencies | — | The build begins |

---

## The build loop

| Command | What it does | When |
|---|---|---|
| **`/start`** | Loads the rules, detects the phase, reads the real state, briefs in under twenty lines. Starts nothing | Sitting down · after `/clear` · after time away |
| **`/next`** | Decides the single best next action and why. **Allowed to say it isn't code.** Recommends; doesn't start | Any time you want direction |
| **`/work`** | Decides *and* runs the ceremony on your yes: claims, branches, reads the spec, then builds | Every time you start building |
| **`/spec <topic>`** | What the specification actually says — quoted, with what it *doesn't* cover | The moment you're about to assume something |
| **`/review`** | The gap between green CI and actually right: spec drift, missing states, silent failure, PII in logs | Before pushing anything that matters |
| **`/audit <ID\|milestone>`** | **Is what we marked done actually done?** Clause by clause; moves failures back | End of a milestone; before a number matters |
| **`/test`** | Runs the suite, reads the failures, says what's actually broken | After a change; when unsure the suite protects the risk |
| **`/secure`** | **Proves** tenant isolation with trespass, then reviews auth, secrets, input | Before anything touching data or auth ships |
| **`/ship`** | The production-readiness gate, then deploy | When a milestone is ready to go live |
| **`/wrap`** | Honest state to the tracker, handoff, changelogs, `make check`, commit | Stopping, even for an hour. **Especially before `/clear`** |

---

## Navigation

| Command | What it does |
|---|---|
| **`/status`** | Which phase the whole project is in, what's done, what's next — across the pipeline and the build |
| **`/board`** | The board in a browser: columns by status, what's ready, who's waiting on whom |

---

## The specialists (subagents)

The front of the pipeline is run by these, defined in `.claude/agents/`. You don't call them directly — the commands do — but knowing they exist explains why the research is thorough: each is a focused mind with a clean context and one job.

| Agent | Owns | Refuses to |
|---|---|---|
| **business-analyst** | narrative, positioning, business model, unit economics | invent a market size or a moat that isn't there |
| **market-researcher** | market sizing, the competitor field, the wedge | copy a competitor without saying why you win |
| **product-manager** | the PRD, user stories, metrics, every screen state | leave a state, error, or edge case unspecified |
| **tech-architect** | architecture, stack, data model, the build roadmap | pick a stack it can't justify, or a plan out of order |
| **feasibility-auditor** | the cross-check of all three plans | pass a plan for want of checking |
| **code-reviewer** | what a grep can't find, before a push | approve something adjacent to the spec |
| **qa** | tests that cover the risk, not the happy path | call a thing tested when the risk isn't |
| **security-auditor** | the permission and data boundaries | assert isolation when trespass can prove it |

---

## What runs on its own

No command needed; the hooks handle it.

| When | What |
|---|---|
| A session opens | The phase, the branch, the claims, the tracker state, what's ready |
| **Every message** | The rule preamble — the operator rules and the rules left to judgement |
| Before a file is written | The secret scan |
| After a file is written | Format and lint |
| A session ends | A check that the tracker was updated, the handoff written, nothing left uncommitted |
| A push to `main` | **Refused** — work lands through a branch and a PR |

---

## The Make targets

| | | |
|---|---|---|
| **`make check`** | The fast gates — no-placeholders, boundaries, ownership, tracker, **trespass** — in seconds | **Before every push** |
| `make verify` | Everything CI runs, incl. lint, types, tests | Before anything large |
| `make secure` | trespass on the schema | Part of `/secure` |
| `make setup` | Hooks and first-time setup | Once per machine |
| `make board` | The board, same as `/board` | — |
| `make gen` | Regenerate anything generated, from its source | After changing a generator's source |
