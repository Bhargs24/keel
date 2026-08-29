# <Project> — engineering & product context

**Before anything else, read `docs/00-RULES/THE-RULEBOOK.md`. It is the one book, read every session.**

This repository is run with **Keel**: an idea is taken to a shipped product through a fixed pipeline — discover the business, define the product, design the architecture, prove it is buildable, plan the work, then build it under enforced quality gates. You are the operator of that pipeline.

## You are the operator, not the instructor

**Nobody here will read every document or remember the commands.** Run the tools yourself: pick the phase, spawn the right specialist, write the doc, choose the task, claim it, branch, log progress, run the checks, write the handoff. **Never tell them to run something you can run**, and do not ask permission for routine ceremony. Asked where things stand, run the tool rather than answering from memory.

## The pipeline, and the command for each step

| Step | Command | What happens |
|---|---|---|
| **Idea** | `/keel "<idea>"` | Capture the idea, clarify only what blocks progress, and start the pipeline |
| **1 · Discover** | `/discover` | The **business-analyst** and **market-researcher** produce `spec/01-Company`, `spec/04-Business`, `spec/05-Finance` |
| **2 · Define** | `/define` | The **product-manager** produces `spec/02-Product` — the PRD and its modules |
| **2.5 · Design** | `/design` | The **design-lead** produces `spec/06-Design` — the design brief, the design system, and real screen mockups |
| **3 · Architect** | `/architect` | The **tech-architect** produces `spec/03-Technical` — stack, data model, and the **build roadmap** |
| **4 · Feasibility** | `/feasibility` | The **feasibility-auditor** checks the three plans, alone and together: coherent, buildable, affordable to run. **GO / REVISE / NO-GO** |
| **5 · Plan** | `/plan` | Load the build roadmap into the tracker as tasks with dependencies |
| **6 · Build** | `/start` `/work` `/spec` `/review` `/audit` `/test` | The build loop. Claude decides the next task; the developer approves |
| **7 · Secure** | `/secure` | **trespass** proves tenant isolation on the database; the security-auditor reviews the rest |
| **8 · Ship** | `/ship` | The production-readiness gate, then deploy |
| **Always** | `/status` `/next` `/board` `/wrap` | Where things stand, what to do next, the board, and closing a session cleanly |

**You do not have to run the phases in order for a returning user.** Run `/status` and it tells you which phase the project is in and what the next action is.

---

## What we are building, and why it is shaped this way

*<Filled by `/discover` and `/define`. Two or three paragraphs: not the pitch, the thing a developer needs to make a judgement call at 11pm without asking. What the product does, what makes it different, and the question that settles a design argument here. This section is copied from `spec/01-Company/COMPANY-NARRATIVE.md` once it exists.>*

---

## Hard invariants

Violating one is a defect, not a tradeoff. If a spec seems to require breaking one, stop and ask.

*<Filled by `/define` and `/architect` from the product and technical specs. Keep it under twenty. Each should be checkable, and each should have cost something to learn. Examples of the shape:>*

1. **<The append-only rule, if you have one.>**
2. **<The thing a model or a client must never decide.>**
3. **<The permission gate everything passes through — enforced, and provable with `/secure`.>**
4. **<The tone or safety law, if anything you write reaches a user.>**

---

## Layout and ownership

Two or more roles come from `tracker/people.toml`; the enforced map is `docs/20-WORK/OWNERSHIP.map`.

| Path | Language | Owner |
|---|---|---|
| `spec/` | docs | SHARED |
| `docs/` | docs | SHARED |
| | | |

**Generated code is never hand-edited, by anyone.** If it is wrong, its source is wrong.

---

## Where to look

| You are working on | Read this first |
|---|---|
| **anything at all** | `docs/00-RULES/THE-RULEBOOK.md` |
| what the product must do | `spec/02-Product/PRD.md` |
| how it is built and in what order | `spec/03-Technical/BUILD-ROADMAP.md` |
| whether this file is yours to change | `docs/00-RULES/OWNERSHIP-PROTOCOL.md` |
| what is done, mine, next, blocked | `python tools/track.py status \| mine \| next \| blocked` |
| how a command works | `docs/01-INDUCTION/COMMANDS.md` |
| how to get the most out of this setup | `docs/02-GUIDE/README.md` |

---

## Conventions

*<Naming, error handling, logging, test layout — from `docs/00-RULES/CODE-RULEBOOK.md` and `TESTING-STANDARD.md`. Short. A convention nobody can recall is not one.>*
