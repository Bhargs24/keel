# <Project>, engineering context

**Before anything else, read `docs/00-RULES/THE-RULEBOOK.md`. It is the one book, read every session.**

## You are the operator

**Nobody here will read every document or remember the commands.** Run the tools yourself: choose the task, claim it, branch, log progress, write the handoff, run the checks. **Never tell them to run something you can run**, and do not ask permission for routine ceremony. Asked about state, run the tool rather than answering from memory.

## Every session

1. `/start`. The `SessionStart` hook has already loaded the state.
2. `/work` to choose and begin. **Claude decides, the developer approves.**
3. Branch `<person>/<TASK-ID>-<slug>`. A branch without the prefix fails CI.
4. `/wrap` before stopping.

---

## What we are building, and why it is shaped this way

*<Two or three paragraphs. Not the pitch: the thing a developer needs in order to make a judgement call at 11pm without asking. What the product does, what makes it different, and the question that settles a design argument here.>*

---

## Hard invariants

Violating one is a defect, not a tradeoff. If a spec seems to require breaking one, stop and ask.

*<List them. Keep it under twenty. Each should be checkable, and each should have cost somebody something to learn. Examples of the shape:>*

1. **<The append-only rule, if you have one.>**
2. **<The thing a model or a client must never decide.>**
3. **<The permission gate everything passes through.>**
4. **<The tone or safety law, if anything you write reaches a user.>**

---

## Layout and ownership

Two roles come from `tracker/people.toml`; the enforced map is `docs/20-WORK/OWNERSHIP.map`.

| Path | Language | Owner |
|---|---|---|
| | | |

**Generated code is never hand-edited, by anyone.** If it is wrong, its source is wrong.

---

## Where to look

| You are working on | Read this first |
|---|---|
| **anything at all** | `docs/00-RULES/THE-RULEBOOK.md` |
| whether this file is yours to change | `docs/00-RULES/OWNERSHIP-PROTOCOL.md` |
| what is done, mine, next, blocked | `python tools/track.py status \| mine \| next \| blocked` |
| how a command works | `docs/01-INDUCTION/COMMANDS.md` |

---

## Conventions

*<Naming, error handling, logging, test layout. Short. A convention nobody can recall is not one.>*
