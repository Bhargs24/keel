# Start here

*Class: **LIVING** · Last-updated: · Owner: <who>. If you read one page before using this, read this one. It works whether you're an engineer or have never written a line of code.*

You have an idea. You have a subscription to an AI coding tool (Claude Code, Cursor, Codex - anything that reads files and runs commands). This turns the first into a shipped product, without it turning into a mess.

## The one thing to understand

**You don't drive the tools. Claude does.** You say what you want in plain words; Claude picks the next step, runs it, and tells you in one line what happened. Your job is to make decisions when it surfaces them and to say "yes, go" - not to remember commands or administrate a process.

## The whole thing in three moves

1. **Type `/keel "<your idea>"`.** One or two sentences. Claude captures it and starts.
2. **Approve each step.** Claude researches the business, defines the product, designs the build, and audits whether it all holds together - pausing at each gate to show you what it found and ask before it goes on. When something's genuinely your call (a name, a budget, a hard trade-off), it asks. Otherwise it proceeds.
3. **When it says GO, it builds** - task by task, testing and securing as it goes, telling you what's next whenever you ask with `/next`.

That's it. Everything below is detail you can reach for when you want it.

## What's happening under the hood

Behind those three moves is a real 0→1 process - the one good founders and teams follow, made automatic:

- **Discover** - is there a real business here? A market sized honestly, competitors mapped, a wedge that's actually defensible, and the numbers (what it costs to build and to run).
- **Define** - what exactly is the product? A proper spec: every screen, every state, every edge case, so nothing gets invented later.
- **Architect** - how is it built, and in what order? A justified tech stack and a build plan where nothing depends on something built later.
- **Feasibility** - does it all hold together? An outside audit of the three plans, alone and together, with a **GO / REVISE / NO-GO** verdict.
- **Build → Secure → Ship** - the disciplined build, with quality gates that don't let corners get cut, a security step that *proves* users can't see each other's data, and a production-readiness gate before it goes live.

## If you already have a spec

Skip the front half. Drop your existing docs into `spec/`, run `/plan` to load the build plan, and `/work` to start building.

## The three commands to remember

> **`/start`** when you sit down. **`/next`** to find out what to do. **`/wrap`** when you stop.

Everything else, Claude reaches for on your behalf. The full list is in [COMMANDS.md](COMMANDS.md); how to get the most out of it is in [../02-GUIDE/README.md](../02-GUIDE/README.md).

## The one rule that protects you

Nothing here asks you to trust that the work is right. **"Done" is verified, not declared** (`/audit` checks it against the written definition of done), and **"secure" is proven, not assumed** (`/secure` runs a tool that either proves no user can reach another's data, or hands you the exact query that breaks it). When the number matters - to a customer, an investor, yourself - it's a number you can trust.
