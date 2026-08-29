# The commands: how to actually work here

*Class: **LIVING** · Last-updated: 2026-08-29 · Owner: founder. For everyone on the team. Seven commands. **You do not need to read the rulebook to work here — Claude reads it for you.** This explains each one properly: what you type, what happens, what comes back, what it refuses, and when to reach for something else.*

> ## If you remember nothing else
>
> **`/start`** when you sit down · **`/work`** to begin, with no arguments — **it decides** · **`/wrap`** when you stop.
>
> Three commands. The other four are for when you want them.

---

# `/start`

### What it is for

Landing. You have opened Claude Code and you do not know, or do not remember, where anything stands. **Works identically on your first session and your hundredth.**

### What you type

```
/start
```

Nothing else. No arguments.

### What Claude actually does

1. **Reads six things in order:** `THE-RULEBOOK.md`, your integration document, `CLAUDE.md`, your build plan, **the last two handoff files**, and `NOW.md`.
2. Runs your spec-fetch step, if you have one.
3. **Runs the tracker rather than guessing:** `track status`, `mine`, `next`, `blocked`, plus the branch, the last five commits and the working tree.
4. Writes you a briefing under twenty lines.
5. **Stops.**

### What comes back

Six things, in this order: **where the project is** (done versus total, which milestone) · **what the last session did**, from the handoffs and the commits · **what is in flight** and whether it has gone quiet · **what is ready for you now, with a recommendation and one sentence of why** · **what you are waiting on from the other person, and them from you** · **anything wrong** — on `main`, a branch with no owner prefix, uncommitted work, an empty `spec/`.

It ends with a proposed next task and waits.

### What it will not do

**It will not start work.** No branch, no edit, until you say what you want. That is deliberate: the briefing is often enough to change your mind about what to do next.

### Reach for it when

You sit down. After `/clear`. After a few days away. When you have lost the thread mid-session and want the real state rather than your memory of it.

---

# `/work`

**The one you will use most, and it decides for you.**

### What it is for

**You should not have to hold the sequence in your head.** There are every task, a dependency graph, ten milestones and two people waiting on each other. Deciding what to build next is exactly the kind of thing a person does badly and a machine does well, so `/work` does it.

### What you type

```
/work
```

**No arguments.** Claude works out what should be built next and tells you why.

You can still name something:

```
/work T-001
/work let's do the event schemas
```

It will run the same procedure and **say plainly if your choice is not the right next thing** — but if you repeat it, it does it. You may have a reason it does not know.

### It verifies the ground before adding to it

This is the part that matters, and it happens before any recommendation.

**1 · Is anything already in flight?** If a task is `doing` or `blocked`, **that is the answer.** Finish it, unblock it, or hand it over. Two half-finished things are worth less than one finished one.

**2 · Is what is marked done actually done?** It audits the recent completions **and every dependency of the task it is about to recommend**, against each one's written `Test / DoD`. If a dependency is done-in-name-only, **that becomes the next task** and it gets moved back with the failing clause logged.

> **Building on a task that is done in name only is the most expensive mistake available**, because everything after it inherits the gap.

**3 · Is anything out of order?** A task done whose dependency is not. Work started in a later milestone while an earlier one has open items. A screen built before the projection it reads.

**If any of that is bad, there is no recommendation.** Fixing the ground is the answer.

### How it chooses, when the ground is solid

Six rules, in order. An earlier one beats a later one.

1. **Earliest milestone first.** Never M2 while M0 has open work.
2. **What unblocks the other person.** A blocked person produces nothing, so this is weighed heavily.
3. **Benches before what they gate.** No capture mode is wired before its bench is green.
4. **The critical path to this milestone's deliverable**, read from your roadmap.
5. **Risk first within a tier.** Between two equal tasks, the one that would **invalidate more later work if it turns out wrong.** Finding that out early beats finishing something safe.
6. **Then size.** Prefer the one that finishes.

### Then it checks the choice against everything the tracker does not know

The roadmap, so the task matches what the milestone is meant to deliver. your integration document, for the seam and the ownership map. **The last handoff**, in case the previous session left a reason to do something else. your open-decisions list, for an open decision or a missing account the work will hit halfway through. And the unassigned work — the content, the design, the spikes, all on the critical path with nobody on them.

> **If the best next action is not code, it says so.** Sometimes the honest answer is *"the most valuable thing today is not this branch, it is a hire, or an experiment that needs real data and no branch."* **It will not recommend a task just because a task is what you asked for.**

### What comes back

Under fifteen lines: **the verdict on the ground** · **the task it chose and which rule decided it** — *"it unblocks four of Sam's tasks"*, *"it is the only M0 item left on the critical path"* · **the runner-up**, so you can overrule it with information · **what it will touch and what done looks like** · **anything that will bite.**

Then it waits for a yes.

### On yes, it runs the whole ceremony

Claims it in `NOW.md` and commits · `track start` · branches as `<person>/<TASK-ID>-<slug>` · your spec-fetch step if needed · reads the step's full block and the spec it points at · **says what it is about to do, and anything in the spec that looks wrong** · enters plan mode first if the blast radius is above T0.

Then builds, logging to the tracker as it goes.

### What it refuses

**A task whose dependencies are unfinished.**

```
T-002 depends on unfinished work: T-001 (alex, todo)
```

**That refusal is the point**, not an obstacle. It names the task, the owner and the status, and offers the nearest thing that is ready.

**And silently editing the other person's area.** It will say so and offer to look rather than change.

### Reach for it when

**Every time you start work.** That is the whole idea: you do not decide, you approve.

---

# `/wrap`

### What it is for

Stopping without leaving a mess for the next session — which is often you, three days later, with no memory of any of it.

### What you type

```
/wrap
```

### What Claude actually does

1. **Logs the honest state** to the tracker. Half-done is fine and gets said as half-done.
2. **Moves the task**: `review` if it needs eyes, `done` if finished, `block` if stuck.
3. **If it is done, it prints what that unblocks** and puts it in `NOW.md`, so the other person sees it without being told.
4. **Writes the handoff** to `docs/40-HANDOFF/<date>-<slug>.md`.
5. **Changelogs every changed file**, and fixes any document the work contradicted.
6. Runs `make check`.
7. **Commits** with a message that says *why*, not what the diff already shows.

### The handoff has four parts, and the last one is the point

**Done** — what actually landed. **Half-done** — what is in flight and exactly where it stops. **Next action** — one sentence, specific enough to start from cold. And:

> **What I know that is not written anywhere.** The dead ends. The thing the spec got wrong. Why a decision went the way it did.

Everything else can be reconstructed from the diff. **That cannot**, and it is the difference between picking up where you left off and starting again.

### Reach for it when

You are stopping, even for an hour. **Especially before `/clear`.**

---

# `/spec`

### What it is for

Finding out what the specification actually says, instead of guessing. There are **your whole specification set** with their states, actions and backend calls.

> **Guessing where a spec exists is the most expensive mistake available in this repository.**

### What you type

```
/spec BE-005              a build step
/spec PA-12               a screen
/spec order.placed        an event
/spec consent             a topic
```

### What comes back

**What it is**, in plain language · **the exact requirements**, including every state · **what it depends on and what depends on it** · **the rules that bind it** — invariants, the anti-anxiety laws, the consent gate · **what the spec does not say**, stated plainly rather than filled in · **the paths it read**, so you can go deeper.

It **quotes the spec where the wording matters** rather than paraphrasing a rule into something softer.

### Reach for it when

You are about to assume something. When a spec seems to contradict another. Before arguing with Claude about how something should behave — usually one of you is right and the spec settles it.

---

# `/review`

### What it is for

The gap between **"CI is green"** and **"this is actually right."** `make check` runs the mechanical gates; this looks for what a grep cannot find.

### What you type

```
/review
```

Run it on your branch, before pushing.

### The eight things it looks for

1. **Does it do what the step said**, or something adjacent? Compared against `Delivers` and `Test / DoD`. **The most common and most expensive failure here.**
2. **Spec drift, including missing states.** Loading, empty, **below-confidence**, error, offline, thin-data are part of the screen. **A missing state is a missing feature.**
3. **The invariants.** Whatever `CLAUDE.md` lists as an invariant. Those are defects, not tradeoffs.
4. **Silent failure.** A bare `except`, an ignored error return, no handling for a timeout or a partial write.
5. **PII in a log line.** Ids, lengths, hashes and confidences only.
6. **Tests that cover the risk**, not only the happy path. Append-only work means idempotency and replay.
7. **Things left behind.** Debug prints, commented-out code, config that only works on your machine.
8. **Blast radius.** What else reads, writes, documents or tests this, and was any of it updated?

### What comes back

Findings as **must fix before push**, **should fix**, **worth knowing** — each with the file, the line, and **the concrete failure it causes.**

**If it finds nothing it says so, and says what it checked.** A review that always finds something is as useless as one that never does.

### Reach for it when

Before pushing anything that touches the ledger, consent, auth, or a screen with states. **Not needed for a documentation change.**

---

# `/audit`

### What it is for

**`track done` is self-declared. Nothing verifies it.**

A task can be marked finished with the work half-built, and the tracker will cheerfully report progress that is not real — which is the number you would quote to a school or an investor. **This is the command that makes the number mean something.**

### What you type

```
/audit T-001        one task, in depth
/audit M0            every done task in a milestone
/audit <person>      every done task of one person's
/audit all           everything marked done
```

### Why it can be objective

**The build plan gives every step a `Test / DoD`.** So this is not an opinion about whether something feels finished; there is a written standard per task and the audit walks it.

### The five checks, per task

1. **Does the code exist where the step said it would?** The `Module` field names the file or boundary. **Nothing there means not done, whatever the tracker says.**
2. **Does it meet the definition of done, clause by clause?** It **quotes each clause** and says whether it holds and how it knows. *"Looks fine"* is not an answer.
3. **Do the tests cover the risk**, or merely exist? Append-only work → idempotency and replay. A screen → every state. A calculation → an input the author did not anticipate.
4. **Were the error and logging notes honoured?** The step's Debug notes name the log points, the edge cases and the flag. Silent failure is a defect.
5. **Is the paperwork true?** Changelog written, contradicted documents fixed, `NOW.md` accurate, the task's own log reflecting what happened.

### The four verdicts

| | |
|---|---|
| **DONE** | every clause holds, tests cover the risk, paperwork true |
| **DONE WITH GAPS** | works, but something named is missing. **Each gap listed** |
| **NOT DONE** | a clause does not hold, or the code is not there |
| **CANNOT VERIFY** | it could not be checked. **Why is stated.** Nothing passes for want of checking |

### It does not just report, it acts

Anything **NOT DONE** is moved back to blocked with the failing clause logged on the task. Gaps are logged so they are not lost.

It finishes with **one honest paragraph on whether the progress number can be trusted.** That paragraph is the only reason to run it.

### Reach for it when

**At the end of every milestone** — `/audit M0`. **Before any conversation where the number matters** — a school, an investor, a hiring decision. And whenever you have the feeling that things are moving faster than they should be.

---

# `/board`

### What you type

```
/board
```

Claude starts it and opens the browser. **You never have to remember the command behind it.**

### What you get

Four views. **Board** — five columns by status, colour-coded. **Ready to start** — only tasks whose dependencies are all done. **Waiting on someone** — grouped by whose unfinished work is holding whom up. **Mine** — your own board. Plus search, and filters by person and milestone.

**Click any task** for its dependencies, what it blocks, timestamps, the full log newest-first, and buttons: **Start · Ready for review · Done · Block**. And a note box — anyone can comment on anyone's task, attributed.

### The part that matters

**It writes the same task files the CLI uses.** Git history, the CLI and CI all keep working. Your changes are commits like any others, and you merge them like anything else.

### Reach for it when

You want to see shape rather than read a list. Planning a week. Showing someone where things stand.

---

# What runs without you typing anything

| When | What |
|---|---|
| A session opens | Branch and whether it is legal · claims in `NOW.md` · tracker status · what is ready · who is waiting on whom · a warning if `spec/` is empty |
| **Every message you send** | The rule preamble: operator rules, the ten rules left to judgement, never push to `main` |
| Before any file is written | Secret scan |
| After any file is written | Format and lint |
| A session ends | Tasks in flight with **no log entry today** · uncommitted changes · a missing handoff |
| `git push` to `main` | **Refused**, with the branch-and-PR flow printed instead |

**None of this needs remembering.** Anything a person has to remember is a rule that will eventually be broken.

---

# Make targets

**`make check` is the one that matters.** The fast gates, seconds, no toolchains. Run it before pushing and CI becomes a formality rather than a thing that catches you.

| | |
|---|---|
| `make dev` | your local stack, `.env` created from the template |
| `make dev-down` · `make db-reset` | stop, or wipe and restart |
| your spec-fetch step | fetch the specifications, if they live elsewhere |
| `make verify` | everything CI runs, including lint, types and tests |
| `make gen` | regenerate `packages/shared` from the event schemas |
| `make setup` | **first time on a machine**: hooks, specs, dependencies |

> **Everyone runs `make setup` once on each machine.** It installs the pre-push guard. Until it runs, that guard does not exist for them.

---

# Three habits

**Plan mode for anything large.** `shift+tab` twice. Claude thinks and proposes without touching a file. **The rulebook requires it above T0** — anything touching anything append-only, permissions, or a schema.

**`/clear` between tasks.** A long session drifts and starts contradicting itself. Two clean sessions beat one long one. The pattern is `/wrap`, `/clear`, `/start`.

**Worktrees for two things at once.**

```bash
git worktree add ../proj-t001 <person>/<TASK-ID>-<slug>
```

Separate folder, separate session, same repository. No stashing, no lost context.

---

# Quick reference

**The page to keep open.**

## The commands

| Command | What it is for | You type | When |
|---|---|---|---|
| **`/start`** | Where the project stands, what the last session did, what is ready, what is wrong. Reads the rulebook, your build plan, the handoffs and `NOW.md`, then runs the tracker. **Stops without starting anything.** | `/start` | Sitting down · after `/clear` · after time away |
| **`/work`** | **Decides what to build next.** Verifies nothing before it is half-done, ranks the candidates, checks the choice against the roadmap and the open decisions, recommends one with the reason, then runs the whole ceremony on your yes. | `/work` *(no arguments)* | **Every time you start work** |
| **`/spec`** | What the specification actually says about a step, screen, event or topic. Quotes it where the wording matters and **says plainly what it does not cover.** | `/spec T-042` `/spec permissions` | **The moment you are about to assume something** |
| **`/review`** | The gap between green CI and actually right. Spec drift and missing states, silent failure, PII in logs, tests that only cover the happy path, blast radius. | `/review` | Before pushing anything touching the ledger, consent, auth or a screen |
| **`/audit`** | **Is what we marked done actually done?** Walks each task's written definition of done clause by clause and **moves failing ones back.** Ends on whether the progress number can be trusted. | `/audit M0` `/audit all` | **End of every milestone** · before any conversation where the number matters |
| **`/wrap`** | Closes the session: honest state to the tracker, status moved, handoff written, changelogs, `make check`, commit. | `/wrap` | Stopping, even for an hour. **Especially before `/clear`** |
| **`/board`** | The board in a browser. Columns by status, what is ready, who is waiting on whom, your own board. Click through to logs and buttons. | `/board` | Seeing shape rather than reading a list |

## The Make targets

| | | |
|---|---|---|
| **`make check`** | **The fast gates, seconds, no toolchains** | **Before every push** |
| `make setup` | Hooks, specs, dependencies | **First time on a machine** |
| `make dev` | Postgres and Redis locally, `.env` created | Starting a work session |
| `make dev-down` · `make db-reset` | Stop · wipe and restart | Done, or the local data went bad |
| your spec-fetch step | Fetch the specifications, if they live elsewhere | `spec/` is empty |
| `make verify` | Everything CI runs, including lint, types, tests | Before anything large |
| `make gen` | Regenerate `packages/shared` from the schemas | After changing a generator's source |
| `make board` | Same as `/board` | — |

## What runs on its own

| When | What |
|---|---|
| Session opens | Branch legality · claims · tracker state · what is ready · who is waiting · empty `spec/` warning |
| **Every message** | The rule preamble |
| Before a file is written | Secret scan |
| After a file is written | Format and lint |
| Session ends | Tasks with no log today · uncommitted changes · missing handoff |
| Push to `main` | **Refused** |

## The three habits

| | |
|---|---|
| **Plan mode**, `shift+tab` twice | Required above T0: the ledger, consent, an event payload |
| **`/clear` between tasks** | A long session drifts. The pattern is `/wrap` → `/clear` → `/start` |
| **Worktrees** for two things at once | `git worktree add ../proj-t001 <person>/<TASK-ID>-<slug>` |

## If you remember three things

> **`/start`** when you sit down.
> **`/work`** to begin, with no arguments, and it decides.
> **`/wrap`** when you stop.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
