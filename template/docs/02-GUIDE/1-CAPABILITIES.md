# What your AI tool can do inside Keel, and where it needs you

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. What Keel gives your AI coding tool that it does not have on its own, what each capability does for you, and, just as important, the decisions it hands back. The division is simple: the machine runs the operation, you make the calls.*

On its own, an AI coding tool is a fast, confident coder with no memory between sessions, no plan for what to build, and no judgement about whether the thing is worth building. Keel adds seven capabilities on top of that: a pipeline, a team of specialists, a memory, a schedule, a set of gates, a proof, and a guide. Most people use the coder and leave the other six on the table. This page is what each one does, and where it stops and needs you.

---

## The one idea: it is the operator, not the instructor

**You do not drive the tools. Your AI does.** Inside Keel it is the operator: it picks the phase, spawns the right specialist, claims the task, makes the branch, reads the spec, logs progress, runs the checks, and writes the handoff. It never tells you to run a command it can run itself, and it does not ask permission for routine ceremony. It does the thing, then says in one line what it did.

Where a real human call is needed, a name, a budget, a trade-off with no clean answer, the thing with no undo, it stops and asks one short question. Everything else it runs. **Your attention belongs on the decisions, not the administration.** That is the whole point, and it holds whether you have never written a line of code or you have shipped for twenty years.

---

## The seven capabilities

| Capability | What it is | Lives in | What it does for you |
|---|---|---|---|
| **The pipeline** | eight ordered, gated steps from idea to ship | the commands | turns "an idea" into a spec, a plan, and a proof before any code is written |
| **The specialists** | ten focused AI minds, one job each, clean context | `.claude/agents/` | real research and real documents, not a stub or a summary |
| **The rulebooks** | the laws, read at the start of every session | `docs/00-RULES/` | the code is written against a standard, not a vibe |
| **The tracker** | a dependency-aware backlog, file per task, in git | `tools/track.py`, `tracker/` | knows the next buildable task, so nothing is built before the thing it needs |
| **The gates and hooks** | mechanical checks that fail the build | `tools/`, `.claude/`, `.githooks/` | refuse placeholder code, boundary breaks, secrets, a push to the main branch |
| **trespass** | a formal analyzer for database access rules | `tools/trespass/` | proves no user can read another's data, or hands you the query that breaks it |
| **The guide** | a browser cockpit of the whole journey | `tools/keel.py` | the one next step in plain words, and every document to read |

**The rule of thumb:** the front of the pipeline (research, spec, design, plan) is run by specialists. The build loop is run by the tracker and the gates. The proof is run by trespass. The guide is how a person watches all of it without memorising anything.

---

## The specialists, in a little more depth

Each specialist is a separate AI instance with a clean context and one job, defined in `.claude/agents/`. You do not call them directly; the commands do. Knowing they exist explains why the research is thorough: a mind that only sizes the market is not also trying to hold the data model in its head.

The front four write your documents: **business-analyst** and **market-researcher** for the business case, **product-manager** for the spec, **design-lead** for the design, **tech-architect** for the build plan. The **feasibility-auditor** cross-checks all three plans together and returns GO, REVISE, or NO-GO. In the build loop, **code-reviewer** catches what a linter cannot, **qa** writes tests that cover the risk, and **security-auditor** proves the boundaries. **tool-scout** finds and vets the tools your project needs. Every one of them is bound by the same law: a weakness it names arrives with the fix that closes it.

## The tracker, in a little more depth

The tracker is the shared memory between you and every future session. `/plan` loads your build roadmap into it as tasks with real dependencies. From then on, `python tools/track.py next` only ever shows a task whose dependencies are genuinely met, and finishing one unlocks the next automatically. `track start <ID>` refuses to begin a task whose groundwork is not done, and that refusal is information, not an obstacle. `/board` opens the same picture as a visual board in your browser.

## The gates, in a little more depth

Rules that depend on being remembered fail under deadline. These do not: they run in code. `no_placeholders` refuses a TODO, a stub, or mock data reaching the main branch. `dep_check` refuses a module reaching across a boundary it may not cross. `ownership_check` refuses a change into code it does not own. `trespass` refuses a database policy that leaks. A secret scan runs before every file write, format and lint run after, and a local hook refuses a push straight to the main branch. `python tools/run.py check` runs the fast ones in seconds, so CI becomes a formality that passes.

## trespass, in a little more depth

Broken access control, one user able to read another user's rows, is the single most common way an AI-built app leaks, and the one class ordinary scanners miss, because catching it means knowing who is *supposed* to see what. trespass compiles every row-level-security policy into logic and either proves no user can reach another's data, or hands you the exact query that shows they can. It runs inside `/secure` and in the gates. A proof, not a linter guessing at patterns.

---

## The division of labour

| The machine's job (it just does this) | Your job (only you can) |
|---|---|
| pick the phase, spawn the specialist | give it a real, specific idea |
| write the document, cite the sources | choose: a company, or a project |
| choose the next task and explain why | say who it is for |
| claim, branch, log, run the gates | judge the wedge: is this genuinely different |
| write the handoff, keep the docs true | settle the trade-offs with no clean answer |
| prove the security boundary | approve the steps that have no undo |

---

## Where it genuinely needs you

- **A real idea, not a category.** "A booking tool for pet groomers that stops double-booking" can be researched. "A SaaS app" cannot. The specialists can study a specific thing; they cannot study a vibe.
- **Honest answers, including "I do not know."** `/keel` asks at most a couple of questions, and only ones that change what gets built. "I am not sure who the buyer is yet" is a real answer that shapes the research, and it beats a confident guess the whole plan then rests on.
- **Reading the one-screen summary at each gate.** Every phase ends with a short recap and the single biggest risk it found. That paragraph is where you catch a wrong turn early, while it is still cheap to fix.
- **The approval before anything irreversible.** A public claim, a message to a user, a schema real people have written to. The machine slows down here on purpose and waits for you.
- **Taste, and knowing your user.** The design-lead can produce something distinctive, but you know the person it is for. When it is off, say so, specifically.
- **Treating a refusal as the system working.** When a specialist says "there is no wedge here yet" or the feasibility-auditor says NO-GO, that is not the tool failing. A comfortable wrong answer costs far more than an uncomfortable right one, and by the paired-honesty law it never leaves you at the problem: the fix comes with it.
