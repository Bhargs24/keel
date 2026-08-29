# The Guide — getting the most out of Keel without losing quality

*Class: **LIVING** · Last-updated: · Review-by: · Owner: <who>. How to move fast here without the speed costing you correctness. The thesis: they don't trade off. The same practices that make it fast — a spec that already exists, a plan reviewed before code, tests that verify without re-reading everything, specialists with clean context — are the ones that keep it right. What destroys quality is skipping them to *feel* faster.*

---

## The five things that matter most

1. **Point at the spec, never describe it.** Keel's whole front half exists so that when you build, you cite `spec/…` instead of paraphrasing from memory. A prompt that says "build the onboarding module per `spec/02-Product/prd/M1.md`" produces the thing; a prompt that describes onboarding from memory produces something adjacent to it, and adjacent is the expensive failure.

2. **Let the gate do its job.** When `/feasibility` says REVISE, fix the plan before building on it. When `/audit` says a task isn't done, it isn't — moving it back is the feature, not friction. When `/secure` finds a hole, it's a hole. The gates are cheap; the bug they catch after launch is not.

3. **One session, one task.** Context rot is structural — attention degrades well before the window fills. When a session starts contradicting itself, it's not being difficult; restart it. The pattern is `/wrap` → `/clear` → `/start`.

4. **Plan mode before anything large.** Pour the effort into the plan so the implementation is one-shot. If it goes wrong mid-implementation, re-plan — don't course-correct blindly. `CHANGE-PROTOCOL.md` says which changes require it (anything above T0).

5. **Approve, don't administrate.** Claude runs the ceremony. Your leverage is in the decisions it surfaces — the wedge, the trade-off, the thing with no undo — not in remembering commands. Spend your attention there.

---

## The pipeline, in practice

**Give it a real idea, not a category.** "A booking tool for pet groomers that stops double-booking" beats "a SaaS app". The specialists can research a specific thing; they can't research a vibe.

**Answer the clarifying questions honestly, including "I don't know".** `/keel` asks at most three, and only ones that change what gets built. "I don't know who the buyer is yet" is a real answer that shapes the market research — it's better than a confident guess the whole plan then rests on.

**Read the one-screen summaries at each gate.** Each phase ends with a short summary and the single biggest risk it found. That paragraph is where you catch a wrong turn early, while it's cheap to fix.

**Trust the specialists' refusals.** When the market-researcher says "there's no wedge here yet" or the feasibility auditor says NO-GO, that's the system working. A comfortable wrong answer costs far more than an uncomfortable right one.

---

## The build, in practice

**`/next` before you decide, `/work` when you've decided.** `/next` shows you the recommendation and the reasoning without touching anything; `/work` runs the whole ceremony on your yes. If you disagree with `/next`, tell it why — it may know something you don't, or you may.

**Cite the spec in every build prompt.** This is the single highest-leverage habit. It's the difference between one clean implementation and three regenerate-from-scratch cycles.

**Run `/secure` before anything touching data or auth ships**, not after. A proven boundary is cheap to get before launch and a crisis to fix after. trespass proves it or shows you the exploit — either way you know, instead of hoping.

**Let `/audit` hold the number honest.** Before you tell a customer or an investor how far along you are, run `/audit` on the milestone. Its fourth verdict is *CANNOT VERIFY*, so the progress number means something.

---

## The enforcement layer (why you don't have to remember)

Rules that depend on being remembered fail under deadline. These don't:

| Mechanism | Enforces |
|---|---|
| `UserPromptSubmit` hook | the rule preamble, on **every single prompt** |
| `PreToolUse` hook | blocks a write that carries a secret |
| `PostToolUse` hook | format and lint on every edit |
| `Stop` hook | the tracker updated, the handoff written, nothing left uncommitted |
| `no_placeholders` in CI | no TODO, stub, mock, or "for now" reaches `main` |
| `dep_check` in CI | module boundaries, so the codebase can't rot into a monolith |
| `ownership_check` in CI | who may touch what — so two sessions never quietly overwrite each other |
| `trespass` in CI | a policy that lets one tenant read another's data fails the build |

---

## Working with a teammate (or several AI sessions)

**Ownership is enforced, not requested** (`OWNERSHIP-PROTOCOL.md`). Your branch prefix declares who you are; the map declares who owns what; CI refuses the rest. This is the single most important protection when two people — or ten agent sessions — share one repo, because a "helpful" fix in the other person's area is the failure that happens by default.

**Three documented ways to cross the line** exist for when work genuinely has to: a crossing note, a handoff, or declared joint work. Reach for them rather than reaching into someone else's area quietly.

---

## A note on the tools you add

Skills, plugins, and MCP servers can read files, run commands, and send data outward. **If your product holds user data, this matters.** Nothing third-party goes in without reading what it does, and anything that could touch user data or credentials is a deliberate, owner-approved choice — not a convenience you added at 2am. Three to five focused MCP servers beat twenty; every one puts tool schemas in context and costs the agent focus.
