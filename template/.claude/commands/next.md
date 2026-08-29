---
description: Decide the single best next action and why. Allowed to say the answer isn't code. Recommends; does not start.
argument-hint: [none]
---

**What is the one best thing to do next?** Decide it, show the reasoning, and
wait. This is the lightweight sibling of `/work`: it recommends without running
the ceremony, so it's safe to ask any time.

## Decide

1. **Which phase are we in?** Run `python tools/track.py phase` — it tells you the
   phase and the next command. If the pipeline isn't through feasibility yet, the
   next action is the next phase; run `python tools/track.py docs` to see exactly
   which documents are missing.
2. **If we're building**, verify the ground before recommending more:
   - Anything `doing` or `blocked`? That's the answer — finish it, unblock it, or
     hand it over. Two half-finished things are worth less than one finished one.
   - Is what's marked done actually done? If a dependency of the obvious next task
     is done-in-name-only, **that** is the next task. Say so.
   - Then rank the ready tasks: earliest milestone → what unblocks someone else →
     what gates other work → the critical path → risk first → size.
3. **Consider that the best action may not be code at all** — a decision the
   founder must make, an account that must be provisioned, an audit that should
   run before more is built on a shaky foundation, a spec gap. **If so, say it
   plainly.** Do not recommend a coding task just because one was expected.

## Report, in under ten lines

- **The verdict on the ground** (what's in flight, whether done means done).
- **The one thing to do**, and the rule that decided it — *"it unblocks four of
  the other person's tasks", "it's the only M0 item on the critical path", "the
  feasibility audit is stale and should re-run before we build on the new plan".*
- **The runner-up**, in one line, so they can overrule you with information.
- **What it will touch and what done looks like.**

Then wait. To actually start the recommended build task, they run `/work`.
