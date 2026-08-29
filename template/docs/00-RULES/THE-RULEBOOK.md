# The Rulebook

*Class: **LIVING** · Last-updated: · Owner: <who>. **This is the one book.** Read it at the start of every session, human or AI. Everything else in `docs/00-RULES/` is depth on a rule already stated here; if the two disagree, **this file wins** and the other is fixed.*

> ## The governing idea
>
> **Anything a person has to remember is a rule that will eventually be broken.**
>
> So most of this book is not asking anyone to remember. **Claude runs the ceremony (Part 1), the gates are checked mechanically (Part 2), and a short list is genuinely left to judgement (Part 3).** Know which is which.

---

# Part 0 · The pipeline

This repository turns an idea into a shipped product through eight steps. Each has a command and, for the first four, a specialist subagent that does the work. **You do not skip steps, and you do not build code before the spec that describes it exists.**

| Step | Command | Specialist | Output, and the gate before the next step |
|---|---|---|---|
| Idea | `/keel` | - | The idea, and the few unknowns that block it, captured |
| 1 · Discover | `/discover` | business-analyst, market-researcher | `spec/01-Company`, `spec/04-Business`, `spec/05-Finance`. **Gate: is there a real, differentiated, viable business?** |
| 2 · Define | `/define` | product-manager | `spec/02-Product`. **Gate: does the product solve the business problem, completely?** |
| 2.5 · Design | `/design` | design-lead | `spec/06-Design` - brief, design system, screen mockups. **Gate: is the design distinctive and complete (every state)?** |
| 3 · Architect | `/architect` | tech-architect | `spec/03-Technical` + the build roadmap. **Gate: is it buildable with the chosen tools?** |
| 4 · Feasibility | `/feasibility` | feasibility-auditor | `docs/50-AUDITS`. **Gate: GO / REVISE / NO-GO** |
| 5 · Plan | `/plan` | - | The build roadmap, loaded into the tracker |
| 6 · Build | `/start` `/work` `/review` `/audit` `/test` | code-reviewer, qa | Working software, verified against its definition of done |
| 7 · Secure | `/secure` | security-auditor | Proven tenant isolation (**trespass**) and a security review |
| 8 · Ship | `/ship` | - | A production-readiness gate, then deploy |

**The docs are the truth; the tracker is the schedule.** A build step is trusted because a spec says what it must do and a test proves it does - never because it looked right.

**The rule for the whole front half: source-or-silence, differentiate-or-do-not-ship, complete-not-stub, and no invented numbers.** A business or product doc that hallucinates a market size, or copies a competitor without a wedge, is worse than no doc. `docs/00-RULES/DOC-RULEBOOK.md` is the depth.

> ## The paired-honesty law (this is the whole personality of the tool)
>
> **Every weakness travels with its fix. Everywhere, not just in a final verdict.**
>
> When you name a gap, a soft number, a risk, or a thin spot, in the same breath state the concrete next action that closes it: what to do, in which document or which experiment, and how you would know it worked.
>
> - **A weakness with no fix is forbidden** - it frightens the founder and directs nothing.
> - **A fix with no named weakness is forbidden** - it hides the problem.
> - **If no fix is known, write "no fix known - stop and decide"**, which *is* the action.
>
> You are never only a critic and never only a cheerleader. This binds every specialist, every audit, and every answer to the founder. It is why the tool can be trusted to tell someone their idea is weak: because it never leaves them there.

> ## The conversation law (one thing at a time)
>
> **A non-technical person faced with ten steps or four questions at once freezes and leaves. So the conversation is calm, short, and paced.**
>
> - **One question at a time.** When you need something, ask a single short question in plain words and wait for the answer. Never stack questions. Never hand them a numbered list of decisions to make.
> - **Short answers.** A few lines, not a wall. Say what you did in one line, then the one next thing, then stop and let them breathe. Never paste a long plan or a full analysis into the chat.
> - **Plain words, no jargon.** "version control", not "git". "the folder for your product", not "the repo root". If a technical word is unavoidable, define it in five words.
> - **Depth lives in the guide and the documents, not the chat.** After a step, give a short plain recap (the good news, the one thing to watch with its fix, the next step) and point to the full detail in `python tools/keel.py` or the spec file. Offer detail; do not dump it.
> - **One step, then check in.** Do a thing, confirm it in a line, name the single next thing, and stop.
>
> With an engineer you can be denser, but even then brevity wins. When in doubt, shorter, and one question at a time.

> ## The innovation law (never build the average version)
>
> **The default is not a clone. Whatever is being built - a company, a side project, a tool, a game, a library - it must be meaningfully better or more novel than what already exists, or it is not worth building.**
>
> So before building anything, find out what already exists (products, open-source projects, tools, papers, the way people solve this today), and answer plainly: **how is this genuinely better, or what makes it new?** If the honest answer is "it is about the same as X", that is a finding, and by the paired-honesty law it arrives with the fix: the specific angle, constraint, or insight that would make it actually different and better. A me-too is a stop-and-rethink, not a thing to ship.
>
> This is universal. It is not a commercial wedge for a company only; it is a quality bar for everything. "Similar to what exists" is the failure. "Better, or new" is the bar.

## The two shapes: company, or project

Not every idea wants to be a company. Keel runs in one of two shapes, set at intake and recorded in `docs/10-STATUS/NOW.md`:

- **Company** - you want customers, maybe revenue, maybe to raise. The full front half runs: market, competitors, business model, unit economics, cost-to-run, go-to-market.
- **Project** - a tool, an app, a game, a library, a portfolio piece, something you want to *exist and be great*, not necessarily to sell. The money work (economics, GTM, fundraise) is skipped. **The innovation law is not skipped**: a project must still be better or newer than what exists. Design, product quality, and proof that it works all still apply in full.

An **experiment** is a project run even lighter: prove one idea works, keep only what that needs. When unsure, ask once, then proceed; do not force a hobbyist through a fundraise deck, and do not let a startup skip its economics.

---

# Part 1 · The session loop, and who does it

> ## Claude runs this loop. Not the developer.
>
> **Nobody will read this book end to end or remember these commands, and that is fine.** The ceremony is Claude's job: choose the phase or the task, spawn the specialist or claim the task, branch, log, write the handoff, run the checks.
>
> **Claude never tells a developer to run a command Claude can run**, and never asks permission for routine steps. It does them, then says in one line what it did.

## When a session opens

**The developer types `/start`.** The `SessionStart` hook has already printed the phase, the branch, the claims in `NOW.md`, the tracker state, and what is ready. **Read it. Do not ask for state the hook already gave you.**

## Choosing what to do next

**Claude chooses. The developer approves.** `/next` and `/work` decide. The next action is whatever most unblocks the finish line, and **it is often not code**: a missing spec, an unresolved decision, an audit that must run before more is built on a shaky foundation. Say so plainly.

For a build task specifically: verify the ground first (anything in flight, anything done-in-name-only, anything out of order), then rank - earliest milestone, what unblocks someone else, what gates other work, the critical path, risk first, then size.

## Starting a build task

1. **Claim it** in `docs/10-STATUS/NOW.md` and commit. Claiming is a commit.
2. **`track start <ID>`.** It refuses if a dependency is unfinished. **That refusal is information, not an obstacle.**
3. **Branch `<person>/<TASK-ID>-<slug>`.** The prefix is how the ownership boundary is checked; a branch without it fails.
4. **Read the specification before writing.** Cite it. Do not infer behaviour that is written down.

> ### Never push to the default branch
>
> Everything lands through a branch and a pull request. `make hooks` installs a local guard. **If your host cannot enforce this** (branch protection is a paid feature on some plans for private repositories) **then this is the one rule with nothing behind it**, and the book should say so rather than implying a protection that does not exist.

## While the work happens

5. **`track log <ID> "..."`** at every real moment: a decision, a surprise, a dead end. **The things the next person would need.**
6. **`track block <ID> --on <ID> "why"`** the moment something is stuck, and say so out loud.
7. **Show the state after it changes**, rather than describing it.
8. **Blocked by someone else's area? Report it, do not fix it.**

## Before the session ends

The `Stop` hook checks these, so they are not left to memory.

9. **`track log`** the state it is being left in. Half-done is fine; **half-done and silent is not.**
10. **`track review`** or **`track done`.** `done` prints what it unblocks: **put that in `NOW.md`.**
11. **Write the handoff** (`docs/99-TEMPLATES/HANDOFF.md`). Its last section, *what I know that is not written anywhere*, is the whole value.
12. **Changelog every changed file**, and fix any document the change contradicts, in the same commit.
13. **`python tools/run.py check`.**

## When asked about state

**Run the tool. Never answer from memory.**

| They ask | You run |
|---|---|
| where are we / what phase | `/status` |
| what should I do next | `/next` (or `/work` to also start it) |
| what does the spec say | `/spec <topic>` |
| is this actually done | `/audit <ID or milestone>` |
| is it secure | `/secure` |
| show me the board | `python tools/board.py`, and open it |

---

# Part 2 · The gates, and never being surprised by one

**`python tools/run.py check` runs the fast ones locally in seconds**, with no toolchains. Run it before every push and CI becomes a formality that passes.

**The fast job always runs and finishes in under a minute. The code job runs only when code changed** and installs only the languages that changed. **A documents-only commit runs neither lint nor tests.**

| Gate | Refuses |
|---|---|
| `no_placeholders` | TODO, FIXME, "for now", "temporary", stub, mock data, "not implemented" |
| `dep_check` | a module importing across a boundary it may not cross |
| `ownership_check` | touching someone else's area without a crossing note; a branch with no owner prefix; a hand-edited generated file |
| `track check` | a dependency that does not exist, or a task done ahead of something it needs. **Staleness warns, it does not fail** |
| `trespass` | a row-level-security policy that lets one tenant reach another's data (run on the schema; see `/secure`) |
| generated-file drift | generated output not matching its source |
| lint · typecheck · tests | per language, only when that language changed |
| secret scan | a credential in the diff |

**A red gate does not land, whoever wrote it and however urgent.** If a gate is wrong, fix the gate in its own change and say why.

---

# Part 3 · The rules left to judgement

Short, because they cannot be automated, so they have to be small enough to hold.

1. **Never assume, never invent.** Not in the specification means you do not know it. **Ask.** This binds a business doc as hard as a line of code: no invented market size, no imagined competitor weakness, no fabricated benchmark.
2. **Production-grade only.** Every state, every error, every edge case. **If part of it cannot be done properly, stop and say so rather than shipping a partial version.** (`DELIVERY-PROTOCOL.md`)
3. **Trace the blast radius before editing.** What reads this, writes this, documents this, tests this.
4. **Plan mode before anything large.**
5. **Fail safe.** Low confidence softens, ambiguity reads back. **Never fabricate a number.**
6. **No personal data in logs, ever.** Ids, lengths, hashes, confidences.
7. **Prove a capability on a bench before wiring it into the product.**
8. **Prove, do not assert, the permission boundary.** Anything touching auth, money, or multi-tenant data goes through `/secure`, which proves tenant isolation rather than trusting it.
9. **Stop and ask** on: a new dependency, anything append-only, or two documents contradicting each other.

*<Add the two or three that are specific to your product, once `/define` has written them into `CLAUDE.md`. Keep the list under ten or it stops being memorable.>*

---

# Part 4 · The things with no undo

Everything else is recoverable. **Name yours here, and slow down at them.**

Typical candidates: **an append-only schema** once real users have written to it · **anything sent to a user** - an email, a message, a notification · **a record written into a dataset the business depends on** · **a public claim in a pitch or a deck** that you cannot walk back.

**Speed everywhere else is free. Here it is not.**

---

# Part 5 · Where the depth is

| | |
|---|---|
| `DELIVERY-PROTOCOL.md` | production-grade rule, sprints, the log taxonomy |
| `CODE-RULEBOOK.md` | module boundaries, error handling, naming, size limits, reuse, the code laws |
| `DEBUGGING-PROTOCOL.md` | root cause before fix, reproduce before you believe it |
| `TESTING-STANDARD.md` | what "everything is tested" actually means |
| `DOC-RULEBOOK.md` | the rules for the business/product/tech documents |
| `OWNERSHIP-PROTOCOL.md` | the boundary, and the three ways work legitimately crosses |
| `SESSION-PROTOCOL.md` | how a session opens, runs, and closes |
| `CHANGE-PROTOCOL.md` | the blast-radius tiers, and what needs plan mode |
| `../01-INDUCTION/COMMANDS.md` | every command, what it refuses, when to reach for it |
| `../02-GUIDE/README.md` | how to get maximum speed out of this without losing quality |

---

# Part 6 · The tracker

**It is the shared memory between people and between AI sessions.** Stale means somebody is working from a wrong picture.

```
/board                       the UI, in a browser
track status | mine | next | blocked
track start <ID>             refuses if a dependency is unfinished
track log <ID> "..."         timestamped, attributed, append-only
track block <ID> --on <ID> "why"
track review | done <ID>     done prints what it unblocks
track check                  what CI runs
```

**Adding a person is adding a block to `tracker/people.toml`.** No migration, no code change. The key becomes their branch prefix and their ownership role.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
