# The Rulebook

*Class: **LIVING** · Last-updated: · Owner: <who>. **This is the one book.** Read it at the start of every session, human or AI. Everything else in `docs/00-RULES/` is depth on a rule already stated here; if the two disagree, **this file wins** and the other is fixed.*

> ## The governing idea
>
> **Anything a person has to remember is a rule that will eventually be broken.**
>
> So most of this book is not asking anyone to remember. **Claude runs the ceremony (Part 1), the gates are checked mechanically (Part 2), and a short list is genuinely left to judgement (Part 3).** Know which is which.

---

# Part 1 · The session loop, and who does it

> ## Claude runs this loop. Not the developer.
>
> **Nobody will read this book end to end or remember these commands, and that is fine.** The ceremony is Claude's job: choose the task, claim it, branch, log progress, write the handoff, run the checks.
>
> **Claude never tells a developer to run a command Claude can run**, and never asks permission for routine steps. It does them, then says in one line what it did.

## When a session opens

**The developer types `/start`.** The `SessionStart` hook has already printed the branch, the claims in `NOW.md`, the tracker state, what is ready and who is waiting on whom. **Read it. Do not ask for state the hook already gave you.**

## Choosing what to build

**Claude chooses. The developer approves.** They should not have to hold the whole dependency graph in their head.

**Verify the ground first.** Anything already in flight is the answer. Then check that the dependencies of whatever you are about to recommend actually meet their own definition of done: **building on a task that is done in name only means everything after it inherits the gap.** Then check nothing is out of order.

**Then rank:** earliest milestone · what unblocks someone else · anything that gates other work · the critical path to the current milestone · risk first within a tier · then size.

**If the best next action is not code, say so.** A hire, a decision, an experiment that needs real data and no branch. **Do not recommend a task because a task was asked for.**

`/work` runs all of this.

## Starting

1. **Claim it** in `docs/10-STATUS/NOW.md` and commit. Claiming is a commit.
2. **`track start <ID>`.** It refuses if a dependency is unfinished. **That refusal is information, not an obstacle.**
3. **Branch `<person>/<TASK-ID>-<slug>`.** The prefix is how the ownership boundary is checked; a branch without it fails.
4. **Read the specification before writing.** Do not infer behaviour that is written down.
5. **Check the date** on every document you rely on.

> ### Never push to the default branch
>
> Everything lands through a branch and a pull request. `make hooks` installs a local guard.
>
> **If your host cannot enforce this** (branch protection is a paid feature on some plans for private repositories) **then this is the one rule with nothing behind it**, and the book should say so rather than implying a protection that does not exist.

## While the work happens

6. **`track log <ID> "..."`** at every real moment: a decision, a surprise, a dead end. **Not a diary. The things the next person would need.**
7. **`track block <ID> --on <ID> "why"`** the moment something is stuck, and say so out loud. A silently stalled task is worse than a blocked one, because nobody can help.
8. **Show the state after it changes**, rather than describing it.
9. **Blocked by someone else's area? Report it, do not fix it.** You do not know what they are mid-way through.

## Before the session ends

The `Stop` hook checks these, so they are not left to memory.

10. **`track log`** the state it is being left in. Half-done is fine; **half-done and silent is not.**
11. **`track review`** or **`track done`.** `done` prints what it unblocks: **put that in `NOW.md`.**
12. **Write the handoff** (`docs/99-TEMPLATES/HANDOFF.md`). Its last section, *what I know that is not written anywhere*, is the whole value.
13. **Changelog every changed file**, and fix any document the change contradicts, in the same commit.
14. **`make check`.**

## When asked about state

**Run the tool. Never answer from memory.**

| They ask | You run |
|---|---|
| what is next, what should I do | `/work` |
| where are we, how much is left | `track status` |
| what is blocking me | `track blocked` |
| show me the board | `python tools/board.py`, and open it |
| **is this actually done** | **`/audit <ID or milestone>`** |

---

# Part 2 · The gates, and never being surprised by one

**`make check` runs the fast ones locally in seconds**, with no toolchains. Run it before every push and CI becomes a formality that passes.

**The fast job always runs and finishes in under a minute. The code job runs only when code changed**, and installs only the languages that changed. **A documents-only commit runs neither lint nor tests** — running four toolchains to check a markdown edit is how CI earns a reputation for wasting time.

| Gate | Refuses |
|---|---|
| `no_placeholders` | TODO, FIXME, "for now", "temporary", stub, mock data, "not implemented" |
| `dep_check` | a module importing across a boundary it may not cross |
| `ownership_check` | touching someone else's area without a crossing note; a branch with no owner prefix; a hand-edited generated file |
| `track check` | a dependency that does not exist, or a task done ahead of something it needs. **Staleness warns, it does not fail** |
| generated-file drift | generated output not matching its source |
| lint · typecheck · tests | per language, only when that language changed |
| secret scan | a credential in the diff |

**A red gate does not land, whoever wrote it and however urgent.** If a gate is wrong, fix the gate in its own change and say why.

---

# Part 3 · The rules left to judgement

Short, because they cannot be automated, so they have to be small enough to hold.

1. **Never assume, never invent.** Not in the specification means you do not know it. **Ask.**
2. **Production-grade only.** Every state, every error, every edge case. **If part of it cannot be done properly, stop and say so rather than shipping a partial version.**
3. **Trace the blast radius before editing.** What reads this, writes this, documents this, tests this.
4. **Plan mode before anything large.**
5. **Fail safe.** Low confidence softens, ambiguity reads back. **Never fabricate a number.**
6. **No personal data in logs, ever.** Ids, lengths, hashes, confidences.
7. **Prove a capability on a bench before wiring it into the product.**
8. **Stop and ask** on: auth, permissions, anything append-only, a new dependency, or two documents contradicting each other.

*<Add the two or three that are specific to your product. Keep the list under ten or it stops being memorable.>*

---

# Part 4 · The things with no undo

Everything else is recoverable. **Name yours here, and slow down at them.**

Typical candidates: **an append-only schema** once real users have written to it · **anything sent to a user** — an email, a message, a notification · **a record written into a dataset the business depends on.**

**Speed everywhere else is free. Here it is not.**

---

# Part 5 · Where the depth is

| | |
|---|---|
| `OWNERSHIP-PROTOCOL.md` | the boundary, and the three ways work legitimately crosses |
| `../01-INDUCTION/COMMANDS.md` | every command, what it refuses, when to reach for it |
| `../../CLAUDE.md` | the invariants and the routing table |
| `../99-TEMPLATES/` | handoff, decision record, changelog |

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
