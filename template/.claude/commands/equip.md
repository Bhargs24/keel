---
description: Find and vet the open-source tools, skills, and MCP servers that would help this project, then wire in the safe ones.
argument-hint: [optional need, e.g. "something to test the UI" or leave empty]
---

**Equip the project with the right open-source capabilities - safely.**

$ARGUMENTS

Use the **tool-scout** subagent. It looks at the stack and the product, finds the
tools that would genuinely help (MCP servers the AI can use, Claude Code skills
and plugins, dev and quality tools, libraries), **vets each one for safety**, and
recommends a small, focused set.

## When to run it

- **After `/architect`**, once the stack is known, to set up the project's tooling.
- **Any time a task needs a capability the project doesn't have** ("I need to drive
  a real browser to test this", "I need to talk to the database directly"). Run
  `/equip <what you need>` and the scout finds the safe option.

## The rules the scout holds

- **Vet before recommending. Security first.** These tools can read files, run
  commands, and send data out. Anything that could touch secrets, credentials, or
  user data needs your explicit yes; it is never a default. If a tool's behaviour
  can't be read, it isn't recommended.
- **Few, not many.** Every MCP server costs the AI focus. The scout prefers the
  smallest set that does the job, not the biggest.
- **Recommend, then install on your yes.** Nothing with data access gets wired in
  silently.

## What you get

The scout updates `docs/02-GUIDE/ARSENAL.md` (the project's vetted tooling in three
tiers: install now / consider / skip) and gives you a short, plain recap: the two
or three tools worth adding now, anything that needs your approval because it
touches data, and what to skip. On your yes, it wires the approved ones in.

**Keel works with any AI coding tool, but MCP servers and skills are richest in
Claude Code.** For another tool, the scout recommends that tool's equivalent
(Cursor rules, an extension, a CLI), and the libraries and dev tools apply
everywhere.
