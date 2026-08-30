# Arming your project, safely

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. How to get the most out of `/equip` and the tool-scout: the open-source tools, skills, and MCP servers that would genuinely help your project, found and vetted for you. This is the how-to. The actual vetted list for your project lives next door in [ARSENAL.md](ARSENAL.md), and the tool-scout keeps it current.*

---

## You should not have to know which tools you need

The open-source ecosystem around AI coding runs to hundreds of tools, skills, and MCP servers, and most of it is noise for any one project. Working out which few would actually help *your* stack, and which of those are safe to trust with your files and your data, is real work. **`/equip` does it for you.**

Run it and Keel sends the **tool-scout**, a specialist whose whole job is this: it reads your stack (`spec/03-Technical/TECH-STACK.md`), your product, and your data model, finds the tools that would genuinely help, **vets every one for safety**, and recommends a small, focused set. It updates the project's ledger, [ARSENAL.md](ARSENAL.md), and on your yes it wires the safe ones in.

---

## When to run it

- **After `/architect`**, once the stack is known. This is when the project's tooling gets set up for the first time.
- **Any time a task needs a capability you do not have.** "I need to drive a real browser to test this." "I need to talk to the database directly." Run `/equip <what you need>` and the scout finds the safe option for that specific need, rather than you guessing at a package name.

---

## The first principle: few, not many

**Every MCP server puts its tool schemas into the AI's context, on every task, and costs it focus.** This is the most common self-inflicted wound in the ecosystem: twenty servers installed, each one making every prompt a little duller. The sweet spot is a handful, three to five, not twenty.

So the scout is biased toward *less*. It prefers the smallest set that does the job, and it will tell you plainly when the honest answer is "you do not need a tool for this; what you have is enough." A tool that saves five minutes once but costs the agent focus on every task afterward is a net loss. The best arsenal is small and sharp. When in doubt, leave it out.

---

## The safety bar, run for every candidate

Skills, plugins, and MCP servers can read your files, run commands, and send data outward. If your product holds user data, this matters. Nothing goes into your arsenal without passing the vetting checklist (it lives in full in [ARSENAL.md](ARSENAL.md)):

- **What does it actually do?** Read its README, and for anything with access, its source. If you cannot tell what it does, it does not go in.
- **What permissions does it need?** File read, command execution, network. Least privilege wins.
- **Does it reach data or credentials?** If it can see secrets, user data, or the database, adding it is a **deliberate, owner-approved decision, never a default.**
- **Does it phone home?** Any telemetry or outbound calls, and to where.
- **Is it maintained and used?** Recent commits, real adoption, an open license.
- **What does it cost the agent?** Is the value worth the focus it takes on every task?

**The rule that binds the whole thing:** a tool that could touch this project's data or credentials never enters silently. The scout reads it, sizes its reach, and gets an explicit yes from you first. It recommends; it does not install data-touching tools on its own.

---

## The three tiers

The scout sorts everything it finds into three tiers in [ARSENAL.md](ARSENAL.md), so a decision is made once and not re-argued later:

| Tier | Means |
|---|---|
| **Install now** | clear value, safe, low context cost. Wire it in. |
| **Consider** | useful, but a trade-off (context cost, maturity, narrow use). Decide per need. |
| **Skip** | recorded, with the reason, so nobody re-litigates it in three weeks. |

The **Skip** tier is quietly the most valuable of the three. A tool that was evaluated and rejected, with the reason written down, saves the next person (or the next session) from re-discovering the same dead end.

---

## How a tool actually gets in

The scout recommends; it does not silently install. The flow has four steps, and the order is deliberate:

1. **It finds and vets** the candidates for your stack, and writes them into the tiers with what each one is, its license, its permissions, its data reach, and a one-line safety verdict.
2. **It gives you a short, plain recap:** the two or three worth adding now, anything that needs your approval because it touches data, and the one thing to skip.
3. **On your yes, it wires the approved ones in:** an MCP server into the tool's config, a dev tool installed, a library added.
4. **It records what went in**, so the ledger stays a true account of what your project trusts.

**Scope each tool to where it belongs.** A database connection that only makes sense for the backend does not need to be loaded everywhere; a browser-driver belongs with the code that has a UI to test. Scoping a tool to one project or one area, rather than installing it globally, keeps its reach small and its context cost off the tasks that do not need it. Least privilege applies to tools, not just to code.

---

## It works across any AI tool

MCP servers and skills are richest in Claude Code, where they are native. That does not lock the rest of the ecosystem away from other tools:

- **In Claude Code**, the scout can recommend MCP servers, skills, and plugins directly.
- **In another tool** (Cursor, Codex, and the rest), it recommends that tool's equivalent instead: a Cursor rules file, an editor extension, a command-line tool.
- **Libraries and dev tools** (linters, test runners, CI actions) apply everywhere, whatever your AI tool is.

So `/equip` is useful no matter how you run Keel; it just tailors its recommendations to what your tool can actually load.

---

## What Keel already ships, so you go looking for less

Before you add anything, know what is already in the box. These are plain Python, need no install, and touch nothing outside your repo:

- **The tracker** (`tools/track.py`) and the board (`tools/board.py`): a dependency-aware backlog you already have.
- **The gates** (`tools/run.py check`): no-placeholders, boundaries, ownership, tracker integrity, and tenant isolation, running in seconds.
- **trespass** (`tools/trespass/`): the formal security proof for your database access rules.
- **The guide** (`tools/keel.py`): the step-by-step cockpit.

Most projects need very little on top of this. A browser-driver for UI testing, a documentation server so the AI writes against a current API rather than a remembered one, maybe a read-only database connection for debugging. That is often the whole list. Reach for the scout when a task genuinely needs a capability you do not have, not out of a sense that more tools must be better.

---

## Keeping the ledger honest

[ARSENAL.md](ARSENAL.md) is a living document, not a one-time output. It is the record of what your project trusts and why. Read it before you rely on a tool. When you add or drop something, keep it current, and let the scout maintain it through `/equip` rather than editing the tiers by hand. A tool nobody remembers vetting is a tool nobody has vetted.
