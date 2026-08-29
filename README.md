# A quality base for building with Claude Code

**A working setup for two or more people building a real product through AI sessions, without it turning into a mess.**

> ### Status, honestly
>
> **What is here works and is tested end to end**: the commands, the tracker, the gates, the hooks, the ownership boundary. Verified on a clean repository, including the dependency refusal, the ownership check reading a real roster, and a crossing note clearing a trespass.
>
> **What is not here yet**: this governs a build against a specification. **It does not help you write one.** That half — working out what your project actually needs written down, and producing it with you — is the direction this is heading and is not built. Until it is, **this assumes you already have specifications.**

Not a linter config and not a prompt library. It is the answer to a specific problem: **AI writes code faster than a human can read it, and the bottleneck moves from typing to trusting.** Everything here exists to make trust cheap.

```bash
python install.py /path/to/your/repo
```

---

## The ideas it is built on

You can throw away every file here and keep these. They are the part that matters.

### 1 · Anything a person has to remember is a rule that will eventually be broken

So very little here asks anyone to remember. A rule either **runs automatically**, or is **checked mechanically**, or is on a short list small enough to actually hold.

The test for any new rule: *can this be a check?* If yes, it must be. A rule that lives only in a document will be reasoned past by an AI session and forgotten by a person, usually on the day it mattered.

### 2 · Claude is the operator, not the instructor

Most setups write their rules to a developer who will not read them. **Write them to Claude instead**, and let the developer say what they want.

The developer says *"let's do the rate limiter"*. Claude finds the task, claims it, starts it, branches correctly, reads the specification, and reports in one line. **It never tells them to run a command it can run itself.** Asked where things stand, it runs the tool rather than answering from memory.

### 3 · Choosing what to build next is a machine's job

A person holds a dependency graph badly. `/work` takes no arguments: it verifies nothing before it is half-done, ranks the candidates against the milestone, what unblocks whom, and what would invalidate the most later work if wrong, then recommends one **with the reason visible** and names the runner-up so you can overrule it with information.

**And it is allowed to say the best next action is not code** — a hire, a decision, an experiment. It will not recommend a task merely because a task was asked for.

### 4 · "Done" must be verified, not declared

Marking something done is self-reported, and self-reported progress is the number you end up quoting to somebody who matters.

`/audit` walks a finished task against its **written definition of done**, clause by clause, and moves it back if it does not hold. Its fourth verdict is **CANNOT VERIFY**, so nothing ever passes for want of checking. It ends on one honest paragraph: **can the progress number be trusted?**

### 5 · The boundary between people is a check, not a courtesy

An AI session has no sense of whose work it is standing in. Asked to fix the console it will reach into the API, because from inside the session that is the shortest path — conflicting a branch mid-flight and routing review past whoever understands the code.

**So ownership is enforced.** The branch prefix declares who you are, a map declares who owns what, and CI refuses the rest. **Three documented ways to cross** exist for when work genuinely has to: a crossing note, a handoff, or declared joint work.

### 6 · Prove a capability on a bench before wiring it in

Build a feature into the product and test it there, and every failure is ambiguous: the model, the adapter, the data, the UI, the network? **On a bench there is one variable and one number.**

A spike answers a question and is deleted. **A bench is permanent** and becomes the regression suite that re-proves the capability whenever a model or a library moves.

### 7 · Fast local gates, so CI is never the first place you learn something is wrong

CI that is slow and punishing teaches people to ignore it or work around it, which is worse than no CI.

`make check` runs the instant checks locally in **seconds**, and CI runs the same ones. The heavy per-language jobs run **only when that language changed**, and a documents-only commit runs neither lint nor tests. **CI becomes a formality that passes.**

### 8 · The handoff carries what is not written anywhere else

Every session ends with a handoff, and its last section is the whole point:

> **What I know that is not written anywhere.** The dead ends. The thing the specification got wrong. Why a decision went the way it did rather than the obvious way.

Everything else can be reconstructed from the diff. That cannot, and it is the difference between resuming and restarting.

---

## What is in the box

### Seven commands

| | |
|---|---|
| `/start` | Where things stand, what the last session did, what is ready, what is wrong. **Stops without starting anything** |
| `/work` | **Decides what to build next.** Verifies the ground, ranks, recommends with reasons, runs the ceremony on your yes |
| `/spec` | What the specification actually says. Quotes it, and **says plainly what it does not cover** |
| `/review` | The gap between green CI and actually right: spec drift, silent failure, personal data in logs, happy-path-only tests |
| `/audit` | **Is what we marked done actually done?** Clause by clause, and it moves failures back |
| `/wrap` | Honest state to the tracker, handoff, changelogs, checks, commit |
| `/board` | The board in a browser |

### A tracker that is files in git

One markdown file per task: a small header and an append-only log. **No database, no hosting, no auth**, works on day one. Git gives history, timestamps and attribution for free, Claude reads and writes it natively, and two people editing different tasks never conflict.

`tools/track.py` is the CLI. `tools/board.py` is a local web UI over the same files, on the standard library, **no dependencies**. Both refuse to start a task whose dependencies are unfinished, and report what a completion unblocks.

**Adding a person is adding a block to `tracker/people.toml`.** The key becomes their branch prefix and their ownership role.

### Gates that run themselves

`no_placeholders` (no TODO, stub, mock data, "for now") · `dep_check` (module boundaries) · `ownership_check` (whose files are whose) · `track check` (dependency integrity) · secret scan · and the per-language jobs, path-filtered.

### Hooks

Session open loads the state · **every message carries the rule preamble** · files are scanned before write and formatted after · session end checks the handoff was written · **pushing to the default branch is refused.**

### A document structure that resists going stale

```
docs/00-RULES/       the one book, and depth behind it
docs/10-STATUS/      NOW.md, what is claimed right now
docs/20-WORK/        ownership map, crossings, allocation
docs/30-CHANGELOG/   per file, so two people rarely conflict
docs/40-HANDOFF/     one per session
docs/50-AUDITS/      dated, never edited after the fact
docs/99-TEMPLATES/   handoff, decision record, changelog
```

Two document classes, and the distinction does the work: **LIVING** carries a review date and is expected to change; **SNAPSHOT** is dated and **never edited after that date**. An audit that gets quietly corrected is not a record of anything.

---

## Installing

```bash
python install.py /path/to/your/repo
```

It asks who is on the team, writes the roster and a starting ownership map, installs the git hooks, and **skips anything that already exists** rather than overwriting it, listing what it skipped so you can merge by hand. `--force` to overwrite, `--dry-run` to look first.

### Then fill in four things

| | |
|---|---|
| `CLAUDE.md` | what you are building, the hard invariants, the layout |
| `THE-RULEBOOK.md` Parts 3 and 4 | your judgement rules, and **what has no undo** |
| `docs/20-WORK/OWNERSHIP.map` | real paths, as they appear |
| `Makefile` | lint, typecheck, test and gen for your languages |

**Part 4 is the one people skip and should not.** Name the things in your system with no undo — an append-only schema, anything sent to a user, a record the business depends on — because everything else is recoverable and speed there is free.

---

## What this is not

**Not a framework.** Nothing imports it. Delete any file and the rest still works.

**Not opinionated about your stack.** The Makefile has empty hooks for your languages. The gates are language-agnostic.

**Not a substitute for specifications.** It assumes you have written down how the product behaves. If you have not, `/spec` has nothing to read and `/audit` has no standard to check against. **The tracker is a schedule; the specification is the truth.**

**Not proven at scale.** It was built for two people on one product and is being used there. It should extend to five. Past that, the file-per-task tracker probably wants replacing with something real — everything else should hold.

---

## Where it came from

Built while setting up an actual product, and every piece exists because something went wrong first.

The gates swallowed failures for weeks because `|| true` kept an empty repository green. CI could not run the toolchains it called. Branch protection turned out to be a paid feature. Nobody could run the product locally. An AI session reached into the other person's service because that was the shortest path. A task was marked done that was not.

**None of that was in a plan. All of it is in here now.**
