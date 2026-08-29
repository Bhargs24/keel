# AGENTS.md - how any AI coding tool works in this project

This project is built with **Keel**. Keel works with any AI coding tool. This file
is the universal entry point that non-Claude tools (Cursor, Codex, Aider, Cline,
Windsurf, Gemini CLI, and others that read `AGENTS.md`) should follow. In Claude
Code, the same behaviour is wired in natively through `.claude/` and you can ignore
this file.

## The one thing to read first

**Read `docs/00-RULES/THE-RULEBOOK.md`.** It is the one book: the pipeline, the
laws, and how a session runs. Everything else is depth on it.

## How the work is done: the pipeline

An idea becomes a shipped product through eight steps. Do not build code before the
spec that describes it exists. The full table is in the rulebook, Part 0. In short:

`/keel` (capture the idea) -> `/discover` (business or prior-art + differentiation)
-> `/define` (the product spec) -> `/design` -> `/architect` (+ the build roadmap)
-> `/feasibility` (GO / REVISE / NO-GO) -> `/plan` (load the tracker) -> build loop
(`/work`, `/review`, `/audit`, `/test`) -> `/secure` -> `/ship`.

## The commands are prompt files

Every command lives in `.claude/commands/<name>.md`. **Run the one you need by
reading that file and following it as your instructions for this turn.** For
example, to start: open `.claude/commands/keel.md` and do what it says. The
specialist roles are defined in `.claude/agents/*.md`; when a command says "use the
product-manager subagent", read `.claude/agents/product-manager.md` and adopt that
role and its bar.

## The tools are plain Python (no AI needed)

These work in any environment, with or without an AI:

- `python tools/run.py check` - the quality gates (placeholders, boundaries,
  ownership, tenant-isolation security). Run before every push. (`make check` also
  works on macOS/Linux.)
- `python tools/run.py guide` - the friendly step-by-step cockpit in a browser.
- `python tools/run.py secure` - prove database tenant isolation with trespass.
- `python tools/track.py status | phase | next | docs` - the tracker and the
  pipeline phase. `python tools/track.py phase` tells you the next step.

## The laws that bind every turn

- **Production-grade or not at all.** Real data paths, every state, every error. No
  mocks, stubs, TODOs, or happy-path-only. If it can't be done properly, stop and say so.
- **The paired-honesty law.** Every weakness you name arrives with its fix.
- **The innovation law.** Never build the average version; it must be genuinely
  better or newer than what already exists.
- **The conversation law.** One short question at a time, plain words, short replies;
  the depth lives in the docs and the guide, not the chat.
- **Never push to the default branch. Prove the permission boundary, don't assume it.**

## Best in Claude Code

Keel installs as a Claude Code plugin, so the commands, the specialist agents, the
hooks (rule reminders, secret scanning, format-on-save), and the security gate are
native there. In any other tool, follow this file and the command prompts; the
tracker, the gates, the security proof, and the guide are identical everywhere.
