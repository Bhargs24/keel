# Getting set up

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. What you need, how to install, and how the moving parts fit together: the guide cockpit, the tracker, and the gates. Keel is built to be easy to start. Two things installed, one command to open the guide, and you are moving. It works whether you write code or have never opened a terminal before today.*

---

## 1 · What you need

| | What | Why |
|---|---|---|
| **Python 3.10 or newer** | check with `python --version` | the tracker, the gates, the security proof, and the guide are plain Python |
| **An AI coding tool** | Claude Code is the smoothest fit | the engine that does the building. Cursor, Codex, Aider, and others work too |
| **Git** | check with `git --version` | your work is versioned; the installer can set this up if it is missing |

Nothing else. There is deliberately no build tool from the 1970s to install and no framework to pin; the parts Keel is meant to hide from you are the parts that must never break in your face.

---

## 2 · Install

### The easiest way (recommended for everyone)

```bash
pip install keel-kit
keel init my-product                # the folder for your new product
```

One command in, one command out: the folder exists, version control is set up, the tracker knows your name (from `--name` or your git identity), and the guide is a `python tools/keel.py` away.

### The concierge way (best for a team)

```bash
git clone https://github.com/Bhargs24/keel
cd keel
python install.py ~/my-product
```

The installer is a concierge, not a form. It asks "is it just you building this?" with no jargon, writes the roster and the ownership map from your answers, and offers to open the guide. You do not have to know what any of it means.

### The developer way (install as a Claude Code plugin)

```
/plugin marketplace add Bhargs24/keel
/plugin install keel
```

Then run `python install.py <your-repo>` once to lay down the project structure, and use the commands in that repo. In Claude Code the commands, the specialist agents, the hooks, and the security gate are all native.

> **On Windows?** Everything works. Use `python tools/run.py check` wherever an older doc says `make check`. Keel prefers the Python runner so nothing depends on a tool you may not have.

---

## 3 · The guide cockpit

This is the front door, and for most people it is the only thing they ever need to open:

```bash
python tools/keel.py            # or: python tools/run.py guide
```

Your browser opens to a friendly cockpit:

- a **progress rail** from Idea to Ship, showing where you are;
- one **"your next step"** card, in plain English, with the exact words to copy into your AI tool;
- **every document Keel writes**, readable right there in the browser, click any card;
- a short **"how this works"** panel, so the cockpit explains itself.

**Do the step it shows, and the page moves to the next one on its own.** No refresh, no remembering commands. Open the guide, do the step, repeat, until you have shipped. That is the whole experience.

---

## 4 · The three commands, if you prefer typing

You never have to memorise the full list. If you remember three, remember these:

> **`/start`** when you sit down. **`/next`** to find out what to do. **`/wrap`** when you stop.

Everything else, Keel reaches for on your behalf. The full reference is in [`../01-INDUCTION/COMMANDS.md`](../01-INDUCTION/COMMANDS.md).

---

## 5 · The tracker

Keel ships a real, dependency-aware task tracker: plain Python, one file per task in git, no external dependencies. `/plan` loads your build roadmap into it, and from then on the build leans on it.

```
python tools/track.py status      done vs total, and what state everything is in
python tools/track.py next        only the tasks whose dependencies are truly met
python tools/track.py mine        what is claimed by you
python tools/track.py blocked     what is stuck, and on what
python tools/track.py phase       which pipeline phase, and the next command
python tools/track.py docs        the whole document set as a checklist
```

`next` only ever surfaces a task whose groundwork is finished, so nothing is built before the thing it needs, and completing one unlocks the next automatically. `python tools/board.py` (or `/board`) opens the same picture as a visual board in your browser.

**Adding a person is adding a few lines to `tracker/people.toml`.** No migration, no code change. That key becomes their branch prefix and their ownership role.

---

## 6 · The gates

The gates are the quality floor, and they run in code so they never depend on anyone remembering them.

```bash
python tools/run.py check         the fast gate: seconds, no toolchains. Run before every push
python tools/run.py verify        everything: the fast gate, plus lint, types, tests
python tools/run.py secure        prove database tenant isolation with trespass
```

`check` is the one to build a habit around. Run it before every push and CI becomes a formality that passes.

| Gate | Refuses |
|---|---|
| `no_placeholders` | a TODO, stub, mock data, or "for now" reaching the main branch |
| `dep_check` | a module importing across a boundary it may not cross |
| `ownership_check` | a change into code it does not own, or a branch with no owner prefix |
| `track check` | a dependency that does not exist, or a task done ahead of what it needs |
| `trespass` | a database policy that lets one user reach another's rows |
| secret scan | a credential in the diff |

The fast job always runs and finishes under a minute. The heavier lint, type, and test jobs run only when code actually changed, and install only the languages that changed. **A documents-only commit runs neither lint nor tests.**

### Install the git hooks, once per machine

```bash
python tools/run.py hooks         # or `make setup` on macOS/Linux
```

This installs the local guard that refuses a push straight to the main branch. Work lands through a branch and a pull request. (On some hosts, branch protection is a paid feature for private repositories; where the host cannot enforce it, this local hook is the stand-in, and it catches the accidental push, which is the realistic failure.)

---

## 7 · Using any AI tool

Only the top layer of Keel is tied to a specific tool, and even that has a universal fallback:

- **`AGENTS.md`** at the repo root is the entry point any tool should read first. It points at the one book (`docs/00-RULES/THE-RULEBOOK.md`) and explains that every command is a prompt file.
- **The commands are prompt files** in `.claude/commands/`. To run one in a non-Claude tool, open that file and follow it as your instructions for the turn.
- **`.cursor/rules/keel.mdc`** wires the same behaviour into Cursor.
- **The tracker, the gates, the security proof, and the guide are identical everywhere**, because they are plain Python and need no AI at all.

Best in Claude Code, where it is native; usable anywhere, because nothing is locked to one vendor.

---

## Verify the setup works

- [ ] `python tools/keel.py` opens the guide in your browser
- [ ] `python tools/track.py phase` prints the current phase and the next command
- [ ] `python tools/run.py check` runs and reports green (or names what failed)
- [ ] you have run `python tools/run.py hooks` once, so a push to the main branch is refused
- [ ] in Claude Code, opening a session prints the phase and the recent state on its own
