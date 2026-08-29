# Start here

*Class: **LIVING** · Last-updated: · Owner: <who>. If you read one page before using Keel, read this one. It works whether you are an engineer or have never written a line of code.*

You have an idea. Keel turns it into a real, shipped product, without it turning into a mess, and without you needing to know how any of the machinery works.

## The easiest way: the guide

Open the friendly guide:

```
python tools/keel.py
```

It opens in your browser and shows you, one step at a time, exactly what to do next, in plain English, with the words to copy. You do that step in your AI coding tool, come back, and it shows you the next one. That is the whole experience: **open the guide, do the step, repeat, until you have shipped.**

The guide also lets you read everything Keel writes as it goes: the business case, the product spec, the design, the plan. Click any card to read it.

## What you actually do

1. **Open the guide** (above), or just type your idea into your AI coding tool:
   `/keel "your idea in a sentence"`.
2. **Answer a couple of questions and say "go".** Keel researches the business,
   defines the product, designs it, plans the build, and checks it all holds
   together, pausing to show you what it found and ask before each step.
3. **When it says the plan is good, it builds it,** piece by piece, testing and
   securing as it goes. Whenever you are unsure what is next, the guide tells you.

You approve the decisions. You do not run the machinery. That is the point.

## The one thing to understand

**You do not drive the tools. Claude does.** You say what you want in plain words; Claude picks the next step, runs it, and tells you in one line what happened. When something is genuinely your call (a name, a budget, a real trade-off), it asks. Otherwise it proceeds. Your job is the decisions, not the administration.

## What is happening under the hood

Behind those simple steps is the real 0 to 1 process good founders follow, made automatic:

- **Discover** - is there a real business here? Market, competitors, the wedge, the numbers.
- **Define** - what exactly is the product? Every screen, every state, so nothing gets invented later.
- **Design** - what does it look and feel like? A real design, not a template.
- **Architect** - how is it built, and in what order?
- **Check** - does it all hold together? An honest audit, with a GO / REVISE / NO-GO.
- **Build, Secure, Ship** - the disciplined build, a security step that *proves* users can't see each other's data, and a readiness gate before it goes live.

And whenever Keel finds a weakness in your idea, your product, or your plan, **it never just tells you it is weak. It always hands you the fix.** That is a rule, not a mood.

## If you already have a spec

Drop your docs into `spec/`, run `/plan` to load the build plan, and `/work` to start building.

## The three commands, if you prefer typing

> **`/start`** when you sit down. **`/next`** to find out what to do. **`/wrap`** when you stop.

Everything else, Claude reaches for on your behalf. The full list is in [COMMANDS.md](COMMANDS.md).

## The one promise

Nothing here asks you to trust that the work is right. **"Done" is verified, not declared** (`/audit` checks it against the written definition of done), and **"secure" is proven, not assumed** (`/secure` runs a tool that either proves no user can reach another's data, or hands you the exact query that breaks it). When the number matters - to a customer, an investor, yourself - it is a number you can trust.
