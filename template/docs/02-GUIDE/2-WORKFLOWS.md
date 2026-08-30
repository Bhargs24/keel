# The workflows: running the pipeline and the build loop well

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. The plays Keel runs, and how to run each one well. Each play exists because it closes a specific way AI-assisted work goes wrong. Speed here comes from the plays, not from typing faster.*

---

## The problem every play is designed around

An AI produces a large volume of plausible work, fast. Volume is never the bottleneck. Knowing it is *right* is. Every workflow below buys a verification signal the AI cannot quietly rewrite: a spec it is checked against, a gate it cannot skip, a proof it cannot fake.

| Failure | What it looks like | The play that kills it |
|---|---|---|
| **Guessing at intent** | work that is polished but solves the wrong problem | run the pipeline in order, cite the spec |
| **Context rot** | sharp early, then repeats questions and contradicts itself | session hygiene: `/wrap`, `/clear`, `/start` |
| **Unverified output** | looks right, and nobody can confirm it | the gates, `/audit`, `/secure` |

---

## Play 1 · Run the pipeline in order, the first time

The eight steps run once, in sequence, and each one gates the next. `/keel` captures the idea. `/discover` finds the business (or, for a project, what already exists and how yours is genuinely better). `/define` writes the product spec. `/design` makes it distinctive. `/architect` produces the stack and the build roadmap. `/feasibility` audits all three plans together. `/plan` loads the roadmap into the tracker, and the build begins.

**Do not skip a step, and do not build code before the spec that describes it exists.** A gate that fails is telling you the next action is to fix that phase, not to push forward.

## Play 2 · Give it a real idea, and answer honestly

The specialists can research a specific thing and cannot research a category, so give them one. At intake, `/keel` asks at most a couple of short questions, only ones that change what gets built. Answer them plainly, including "I do not know yet", which is a real answer that shapes the research rather than a guess the whole plan then rests on.

## Play 3 · Read the one-screen summary at each gate

Every phase ends with a short recap and the single biggest risk it found. **That paragraph is the highest-leverage minute in the whole pipeline**, because it is where you catch a wrong turn while it is still cheap. The depth lives in the documents and the guide (`python tools/keel.py`); the chat gives you the recap and points you there.

## Play 4 · Trust the specialists' refusals

When the market-researcher says "there is no wedge here yet", when the product-manager says a state is unspecified, when the feasibility-auditor says NO-GO, that is the system working, not the system failing. By the paired-honesty law, none of these leave you at the problem: the fix travels with the finding. A me-too idea is a stop-and-rethink, not a thing to ship. An uncomfortable right answer is cheaper than a comfortable wrong one, every time.

---

## Play 5 · The build loop: `/next` to decide, `/work` to run

Once you are building, three commands carry the day.

- **`/start`** opens a session. It loads the rules, detects the phase from what is on disk, reads the real state, and briefs you in under twenty lines. It starts nothing.
- **`/next`** decides the single best next action and shows the reasoning, without touching a thing. It is allowed to tell you the best next action is *not* code: a missing spec, an unresolved decision, an audit that must run first. If you disagree, tell it why. It may know something you do not, or you may.
- **`/work`** decides *and*, on your yes, runs the whole ceremony: it claims the task in `NOW.md`, runs `track start`, makes the branch, reads the spec, and builds.

The shape is always the same. It recommends. You approve. It runs. You never hold the sequence in your head; the build roadmap, the dependency graph, and `/next` are what hold it.

## Play 6 · Cite the spec in every build prompt

This is the single highest-leverage habit in the build. A prompt that says "build the onboarding module per `spec/02-Product/prd/M1.md`" produces the thing. A prompt that describes onboarding from memory produces something adjacent to it, and adjacent is the failure that costs three regenerate-from-scratch cycles. When you are about to assume something, run `/spec <topic>` first: it quotes what the specification actually says, and what it does *not* cover.

## Play 7 · Let `/audit` hold the number honest

Before you tell a customer, an investor, or yourself how far along you are, run `/audit` on the milestone. It walks each task against its written definition of done, clause by clause, and moves failures back. Its fourth verdict is *CANNOT VERIFY*, so a "done" that cannot be proven does not get to count. **Building on a task that is done-in-name-only is the most expensive mistake available**, because everything after it inherits the gap.

## Play 8 · Run `/secure` before anything touching data or auth ships

Not after. A proven boundary is cheap to get before launch and a crisis to fix after. `/secure` runs trespass on your database schema and either proves no user can reach another's rows or hands you the exact query that shows they can, then the security-auditor reviews auth, secrets, and input handling. Either way you *know*, instead of hoping.

---

## Play 9 · Session hygiene, against context rot

An AI's attention degrades as its context fills with old decisions and abandoned attempts, and it degrades well before the window is full, so a big context window delays the problem rather than solving it. Learn the symptoms: it asks something you already answered, it proposes an approach it already rejected, it re-reads files it read an hour ago.

**The pattern is `/wrap` then `/clear` then `/start`.** `/wrap` writes the honest state to the tracker and a handoff to disk. `/clear` resets the context. `/start` reconstructs the state from those files in under a minute. One session, one task. When a session starts feeling stupid, it is not a sunk cost to protect; restarting is the cheapest fix available.

## Play 10 · The returning-user flow

You never have to remember where you left off. `python tools/track.py phase` detects the phase from what exists on disk, so it is a fact, not a guess, and `/status` turns that into a short, honest picture: the phase, the one next action, which documents exist and which do not, what is in flight, and anything that has gone wrong (on the main branch, a stale audit, uncommitted work). Sit down, run `/start`, do the one thing it names.

## Play 11 · Company, or project

Keel runs in one of two shapes, set at intake and recorded in `NOW.md`. **Company** runs the full front half: market, competitors, unit economics, cost to run, go-to-market. **Project** skips the money work and keeps everything else. An **experiment** is lighter still: prove one idea works, keep only what that needs. One rule never bends in any shape: the innovation law. It must be genuinely better or newer than what already exists. Matching the rigor to the thing, so a weekend project carries no fundraise deck and a funded startup never skips its economics, is part of the point.

## Play 12 · Working with a teammate, or several sessions

Ownership is enforced, not requested. Your branch prefix declares who you are, `docs/20-WORK/OWNERSHIP.map` declares who owns what, and the `ownership_check` gate refuses the rest. This is the most important protection when two people, or ten AI sessions, share one repo, because a "helpful" fix in someone else's area is the failure that happens by default. When work genuinely has to cross the line, three documented ways exist: a crossing note, a handoff, or declared joint work. Reach for one rather than reaching in quietly.

---

## The daily shape

```
sit down     /start  ·  read the brief  ·  /next to get the one thing
build        /work on the yes  ·  cite the spec  ·  let the gates run
before a     /audit the milestone  ·  /secure anything touching data
  number
stop         /wrap: the tracker honest, the handoff written, the checks green
             then /clear before the next thing (do not roll straight on)
```

**What speed actually comes from:** a spec that already exists so nothing is guessed, a gate the AI cannot skip so nothing rots, a proof the AI cannot fake so security is known, and a returning flow that reconstructs state from disk so no session starts cold. Quality does not trade against speed here. The plays that make it fast are the same ones that keep it right.
