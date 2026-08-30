<div align="center">

# Keel

### Build a real product from one idea, with an AI founding team.

**Keel is an open-source AI product builder that takes you from an idea to a shipped, production-grade product.** It does the market research, writes the business case, defines the product spec, designs the screens, plans the build, then writes and ships the actual code, tested and secured, by driving the AI coding tool you already use (Claude Code, Cursor, Codex, and more).

It is the tool for the part everyone skips: **knowing what to build and why, in what order, and proving it actually works before real users arrive.** And it is easy enough for a non-technical founder and rigorous enough for a senior engineer.

**Building a company or just a project?** Both. Keel runs in two shapes: a full **company** path (market, competitors, unit economics, go-to-market) or a lighter **project** path (skip the money work, just build something great). Either way one rule never bends: **it must be genuinely better or more original than what already exists. Never a clone, never the average version.**

</div>

<p align="center">
<a href="https://pypi.org/project/keel-kit/"><img src="https://img.shields.io/pypi/v/keel-kit?color=2e7d32&label=pip%20install%20keel-kit" alt="Install from PyPI"></a>
<img src="https://img.shields.io/pypi/pyversions/keel-kit?color=2e7d32" alt="Python versions">
<img src="https://img.shields.io/badge/license-MIT-2e7d32" alt="MIT License">
</p>

<p align="center">
<a href="#install-it-start-here"><b>Install</b></a> ·
<a href="#use-it"><b>Use it</b></a> ·
<a href="#easy-by-design"><b>How it feels</b></a> ·
<a href="#how-keel-compares"><b>Compare</b></a> ·
<a href="#faq"><b>FAQ</b></a> ·
<a href="https://github.com/Bhargs24/keel"><b>GitHub</b></a>
</p>

<p align="center">
<img src="assets/cockpit-hero.png" alt="The Keel guide: a progress rail from Idea to Ship, a plain-English next-step card with the exact command to copy, and the document set Keel has written" width="880">
<br><sub>The guide (<code>python tools/keel.py</code>), on a real project: the one next step in plain words, the journey from idea to ship, and every document Keel has written.</sub>
</p>

---

## What is Keel?

Keel is a free, open-source system that turns a one-sentence idea into a complete, buildable, shippable product. Think of it as an **AI founding team in your terminal**: a business analyst, a market researcher, a product manager, a designer, a software architect, a QA engineer, and a security auditor, each an AI specialist that does its part of the 0 to 1 work and hands you a real deliverable.

Most AI tools help you generate a prototype in minutes. Keel helps you build a **real product**: one that is planned, designed, tested, secure, and grounded in an actual business case, using the AI coding tool you already pay for as the engine. You bring the idea and the decisions. Keel does everything else and tells you the single next step at every point.

**Keywords:** AI app builder, idea to MVP, idea to production, build a startup with AI, AI product manager, spec-driven development, AI market research, PRD generator, vibe coding done right, Claude Code workflow, Cursor workflow, open-source AI developer tool.

---

## The magic-wand loop

```mermaid
flowchart LR
    I([Your idea]) --> D
    subgraph R [the specialists do the thinking]
      direction LR
      D[1 Discover] --> P[2 Define] --> DS[3 Design] --> A[4 Architect]
    end
    A --> F{5 Feasibility}
    F -->|revise| D
    F -->|GO| PL[6 Plan] --> B[7 Build] --> S[8 Secure] --> SH([Ship])
    B -.->|next task| B
```

| Step | What happens |
|---|---|
| **1 · Discover** | The business case, or for a project, what already exists and how yours is genuinely better |
| **2 · Define** | The product spec: the target user's psychology, then every screen and every state |
| **3 · Design** | A distinctive design system and real screen mockups, never a template |
| **4 · Architect** | A justified tech stack, the data model, and a dependency-ordered build plan |
| **5 · Feasibility** | An honest audit of all three plans together. **GO / REVISE / NO-GO** |
| **6 · Plan** | The build roadmap becomes a tracked, ordered backlog |
| **7 · Build** | Keel writes and tests the real code, one task at a time |
| **8 · Secure** | It proves no user can read another user's data, then ships |

The research steps each spawn a **specialist AI subagent** that writes a real document, not a stub. The feasibility gate checks all three plans together: is the product coherent with the business, is it buildable with your tools, can you afford to run it? If not, it says `REVISE` and tells you exactly what to fix. And whenever Keel finds a weakness, in your idea, your product, or your code, **it never leaves you there. It always hands you the fix.**

---

## Does Keel actually write the code?

**Yes.** Keel is not just a planner. Once the plan passes the feasibility gate, Keel drives your AI coding tool through the entire build: it picks the next task, writes production-grade code (real data paths, every state, every error, no mocks or TODOs), writes the tests, proves the security, and moves to the next task. It writes the whole product.

What makes Keel different from using a coding agent on its own is the judgment around the code:

- it **works out what to build and why** (the business case and the product spec),
- it **builds in the right order** (a dependency-ordered plan, so nothing is built before the thing it needs),
- and it **proves the result is real** (`/audit` verifies "done" against a written definition of done, and `/secure` proves no user can read another user's data).

Raw coding agents write code fast and guess at the rest. Keel removes the guessing.

---

## Production quality, enforced (not hoped for)

Most AI tools will hand you code full of mock data, `TODO`s, and happy-path-only functions, and call it done. Keel will not. Quality here is enforced by gates that **fail the build**, not by good intentions.

**Gates that run on every change:**

| Gate | What it refuses to let through |
|---|---|
| `no_placeholders` | mock data, stubs, `TODO`s, placeholder or demo code |
| `dep_check` | a module importing across a boundary, or a circular dependency |
| `ownership_check` | a change reaching into code it does not own |
| `trespass` | a database policy that lets one user read another user's rows |
| tracker integrity | a build plan that has drifted from the actual work |

**Laws the code is written against**, in rulebooks the AI reads every session: every error is typed with a stable, greppable code (`VAL_`, `AUTH_`, `NOTFOUND_`, `DEP_`, and so on) and never silently swallowed; no personal data in logs, ever; functions stay small and single-purpose; the same logic is never pasted twice, so a fix is made in one place; a bug is root-caused and reproduced before it is called fixed; and secrets are scanned on every write.

The judgement a linter cannot make is done by a **code-reviewer** specialist before a push: spec drift, silent failures, a missing empty or error state, a test that only covers the happy path. Every weakness it finds arrives with the fix that closes it. That is a law here, not a courtesy.

This is the line between code you can demo and code you can ship.

---

## Works with any AI tool (open or closed)

Keel is built in layers, and only the top one is tied to a specific tool:

| Layer | What it is | Tool it needs |
|---|---|---|
| **The brains** | the rulebook, the pipeline, the specs, the laws | none, they are just Markdown |
| **The tools** | the tracker, the quality gates, the security proof (trespass), the guide cockpit | just Python, works with **no AI at all** |
| **The integration** | slash commands, specialist agents, hooks, the plugin | **best in Claude Code** (native), works elsewhere via `AGENTS.md` |

So: **best with Claude Code**, where the commands, agents, hooks, and security gate are native. But it works with **any AI coding tool**, Cursor, Codex, Aider, Cline, Windsurf, Gemini CLI, open-source or closed, because every command is a prompt file the AI reads, and the repo ships an `AGENTS.md` (the emerging cross-tool standard) plus a Cursor rules file as the universal entry point. And the tracker, the gates, the security proof, and the guide run with no AI at all. Nothing here is locked to one vendor.

---

## Your project's own toolkit, found and vetted for you

You should not have to know which open-source tools, skills, or MCP servers your project needs. **`/equip`** sends a **tool-scout** to find them, for your exact stack: the MCP servers the AI can use, the Claude Code skills and plugins, the dev and quality tools, the libraries. It **vets every one for safety** (what it does, what it can access, whether it touches your data or secrets) and recommends a small, focused set, because piling on twenty tools just costs the AI focus. Anything that could touch your data or credentials is never added without your explicit yes. The vetted list lives in your repo, and the safe tools get wired in for you.

---

## Install it (start here)

### What you need first

1. **Python 3.10 or newer.** Check with `python --version`. Get it from [python.org](https://www.python.org/downloads/) (tick "Add Python to PATH" on the first screen).
2. **An AI coding tool.** [Claude Code](https://claude.com/claude-code) is the smoothest fit. Cursor, Codex, or any tool that reads files and runs commands also works.
3. **Git.** From [git-scm.com](https://git-scm.com/downloads) if `git --version` fails. (Keel's installer can set your project up if this is missing.)

### The easiest way (recommended for everyone)

```bash
pip install keel-kit
keel init my-product      # the folder for your new product
```

That installs Keel and scaffolds a fresh project into `my-product`, with version control set up and ready to go.

Prefer not to use pip? Clone the repo instead. The concierge installer does the same thing and asks "is it just you building this?" with no jargon:

```bash
git clone https://github.com/Bhargs24/keel
cd keel
python install.py ~/my-product
```

Then open the **guide**, which shows you the next step at every point:

```bash
cd ~/my-product
python tools/keel.py
```

Your browser opens to a friendly cockpit: a progress rail from Idea to Ship, one plain-English "your next step" card with the exact words to copy, and every document Keel writes, readable in the browser. It even explains itself, with a short "how this works" panel built in. **Do the step it shows, and the page moves to the next one on its own. No refresh, no remembering commands. Keep going until you have shipped.**

### The developer way (install as a Claude Code plugin)

```
/plugin marketplace add Bhargs24/keel
/plugin install keel
```

Then run `python install.py <your-repo>` once to lay down the project structure, and use the commands in that repo.

> **On Windows?** Everything works. Use `python tools/run.py check` wherever older docs say `make check`. Keel prefers the Python runner so nothing depends on tools you may not have.

---

## Use it

**You do not drive the tools. Keel does.** You say what you want in plain words; it picks the next step, runs it, and tells you in one line what happened. When something is genuinely your call (a name, a budget, a real trade-off), it asks. Otherwise it proceeds.

**The whole thing, in three moves:**

1. **Give it your idea.** In the guide, or by typing `/keel "your idea in a sentence"` in your AI tool.
2. **Approve each step.** Keel researches the business, defines the product, designs it, plans the build, and audits whether it holds together, pausing at each gate to show you what it found.
3. **When it says GO, it builds** the product, task by task, testing and securing as it goes. Ask `/next` any time to see what is next.

**Already have a spec?** Drop your documents into `spec/`, run `/plan`, then `/work`.

**The three commands to remember:** `/start` when you sit down, `/next` to find out what to do, `/wrap` when you stop. Everything else, Keel reaches for on your behalf.

**And you never have to memorize the rest.** The guide shows every command and what it does, right on the screen, with a marker on the one you are up to:

<p align="center">
<img src="assets/keel-commands.png" alt="The Keel cockpit's command reference: every command grouped into the pipeline, the build loop, and anytime, each with a plain-English description, and a you-are-here marker on the current step" width="720">
</p>

Twenty commands, three groups: the **pipeline** (`/keel` through `/plan`), the **build loop** (`/work`, `/review`, `/audit`, `/test`, `/equip`, `/secure`, `/ship`, and more), and the **anytime** navigation (`/status`, `/board`). The full reference with what each spawns is in [`docs/01-INDUCTION/COMMANDS.md`](template/docs/01-INDUCTION/COMMANDS.md).

---

## A tracker that knows what is next

Keel ships a real, dependency-aware task tracker (plain Python, file-per-task in git, no dependencies). `/plan` loads your build roadmap into it; from then on the build loop leans on it:

```text
$ python tools/track.py status
Progress   1/3 done (33%)   todo 2  doing 0  blocked 0  review 0  done 1

$ python tools/track.py next
Ready now
  TODO   T-002   Build the login flow     # T-003 stays hidden: it depends on this
```

`next` only ever surfaces a task whose dependencies are met, so nothing is built before the thing it needs, and finishing one unlocks the next automatically. `/board` opens the same thing as a visual board in your browser:

<p align="center">
<img src="assets/keel-board.png" alt="The Keel task board: columns for todo, doing, blocked, review, and done, with the pipeline strip on top and dependency notes like 'waiting on T-003' on the cards" width="880">
</p>

---

## Easy by design

Keel is built so a first-time builder never freezes. It talks the way a good mentor does: **one short question at a time, in plain words**, and it never dumps a wall of steps on you. The long plans and the details live in the guide and the documents. The conversation stays calm.

<p align="center">
<img src="assets/conversation.svg" alt="Keel asking one short question at a time in plain English, then confirming in a single line" width="820">
</p>

Two rules make this true, and they run on every message:

- **The conversation law:** one question at a time, short plain answers, no jargon, and the depth kept in the guide rather than pasted into the chat.
- **The paired-honesty law:** whenever Keel finds a weakness in your idea, product, or code, it hands you the fix in the same breath. It is never only a critic, and never a wall of problems with no way forward.

---

## How Keel compares

| | Prompt-to-app builders<br/><sub>(Lovable, Bolt, v0, Base44)</sub> | A raw AI coding agent<br/><sub>(Claude Code, Cursor alone)</sub> | **Keel** |
|---|:---:|:---:|:---:|
| Writes working code | Prototype | Yes | **Yes, production-grade** |
| Market and competitor research | No | No | **Yes** |
| A real product spec (PRD) | No | No | **Yes** |
| A distinctive design system | Partial | No | **Yes** |
| Feasibility audit before building | No | No | **Yes** |
| Dependency-ordered build plan | No | No | **Yes** |
| Verifies "done" is really done | No | No | **Yes (`/audit`)** |
| Proves security (no data leaks) | No | No | **Yes (`trespass`)** |
| Uses the AI tool you already pay for | No (locked in) | Yes | **Yes** |
| Open source, yours to keep | No | No | **Yes (MIT)** |

Prompt-to-app builders are great for a quick demo, then you hit the wall: no real spec, no plan, no proof it works, and you are locked into their platform. A raw coding agent writes code fast but guesses at what to build and whether it is right. **Keel gives you the whole path, and you own it.**

---

## What Keel produces

**A complete, professional document set, plus the working product.** Every document is written to a hard rigor standard: deep and exhaustive, not a summary; researched, with every external claim cited inline (source, URL, date) and a Sources list; written to the real professional format for that artifact. This is the difference between Keel and a chatbot that hands you an outline: it writes the actual document.

<p align="center">
<img src="assets/cockpit-full.png" alt="The Keel cockpit on a real project: the whole document map from Discover through Architect, with the Discover set complete and cited" width="620">
<br><sub>A real run: the whole document map, from the business case through the technical plan, each one Keel writes and you can read in the guide.</sub>
</p>

- **Business:** the company narrative, vision and values, positioning against a real moat (the 7 Powers, not hand-waving), market and competitor analysis, unit economics stress-tested with a downside case, a defensibility analysis, a pre-mortem, a financial model (P&L, burn, runway), a fundraise ask, and the real monthly cost to run, rebuilt from prices checked today.
- **Product:** it starts with the person, the target user's psychology and the behaviour the product has to create, not a feature list. Then a master PRD and per-module specs with prioritized, testable requirements, jobs-to-be-done, success metrics, a product roadmap, real-world scenarios, and every screen state, so the product is built around how people actually think and act.
- **Design:** a design brief, a design system (colors, type, components), and real HTML mockups of the key screens, covering every state.
- **Technical:** the architecture, a justified tech stack, the data model, a security and privacy design, the infra and CI/CD, a setup runbook, the accounts to set up, and a dependency-ordered build roadmap.
- **The product itself:** production-grade code, tests that cover the risk, and a security proof, built task by task and tracked in git.

**Scaled to what you are building.** A serious company gets the full set (around thirty documents). A weekend project gets a focused one (the concept, the product, the design, the plan). A side project has no business carrying a fundraise deck, and a funded startup with no unit economics is flying blind. Knowing which one you are, and giving it exactly the rigor it needs, is part of the point.

---

## The specialists

Each is a focused AI mind with a clean context and one job, defined in `.claude/agents/`.

| Agent | Owns |
|---|---|
| **business-analyst** | the narrative, business model, unit economics, the moat, a pre-mortem |
| **market-researcher** | market sizing, the competitor field, the wedge, incumbent-response war-gaming |
| **product-manager** | the target user's psychology and behaviour, then the PRD, prioritized testable requirements, and every screen state |
| **design-lead** | the design brief, the design system, real screen mockups |
| **tech-architect** | architecture, stack, data model, the build roadmap |
| **feasibility-auditor** | the cross-check of all three plans, with a GO / REVISE / NO-GO verdict |
| **code-reviewer** | the gap a grep cannot find, before a push |
| **qa** | tests that cover the risk, not just the happy path |
| **security-auditor** | the permission and data boundaries |
| **tool-scout** | finding and vetting the open-source tools, skills, and MCP servers your project needs |

---

## trespass: security you can prove

Broken access control, one user able to read or delete another user's data, is the single most common way AI-built apps leak, and the one class ordinary scanners cannot catch, because catching it needs to know who is *supposed* to see what.

Keel ships **trespass**, a formal analyzer for Postgres and Supabase row-level security. It compiles every policy into logic and either **proves** no user can reach another's rows, or hands you the exact query that shows they can:

<p align="center">
<img src="assets/trespass-proof.png" alt="trespass output: a policy proven VULNERABLE with a solver counterexample, the exact query that reproduces the leak, and the fix" width="760">
</p>

That is a real run: a policy a developer would plausibly write, proven unsafe by the solver, with the counterexample and the fix. Not a linter guessing at patterns, a proof.

Written from scratch on the standard library, validated against Z3 and a real Postgres, it runs in the gates and in `/secure`, and it fails your build when a policy leaks. Details: [`tools/trespass/README.md`](template/tools/trespass/README.md).

---

## FAQ

*Click any question to open its answer.*

<details open>
<summary><b>Is Keel free?</b></summary>

Yes. Keel is open source under the MIT license. You only pay for the AI coding tool you already use (like Claude Code or Cursor).

</details>

<details>
<summary><b>Do I need to know how to code to use Keel?</b></summary>

No. The guided cockpit shows you the one next step in plain English and gives you the exact words to paste. Keel does the technical work; you make the decisions it surfaces. It is also rigorous enough for professional engineers.

</details>

<details>
<summary><b>Does Keel write the actual code, or just documents?</b></summary>

Both. It writes the full business and product plan, and then it writes and ships the actual product code, tested and secured, by driving your AI coding tool.

</details>

<details>
<summary><b>What AI tools does Keel work with, open source or closed?</b></summary>

Any of them. Claude Code fits most smoothly (Keel installs as a plugin, with native commands, agents, and hooks). It also works with Cursor, Codex, Aider, Cline, Windsurf, Gemini CLI, and any other AI coding tool, open-source or closed, because the commands are prompt files and the repo ships a universal `AGENTS.md` plus a Cursor rules file. The tracker, the quality gates, the security proof, and the guide are plain Python and work with no AI at all. Nothing is locked to one vendor.

</details>

<details>
<summary><b>Does Keel find and set up the right open-source tools for my project?</b></summary>

Yes. `/equip` sends a tool-scout to find the MCP servers, skills, and libraries your specific stack needs, vets each one for safety (what it can access, whether it touches your data), recommends a small focused set, and wires in the safe ones. Anything that could reach your data or secrets is never added without your explicit yes.

</details>

<details>
<summary><b>How is Keel different from Lovable, Bolt, v0, or Replit?</b></summary>

Those generate a prototype from a prompt, then leave you at the wall with no spec, no plan, and no proof it works, locked into their platform. Keel does the research, the spec, the design, the plan, and the proof, and builds with the tool you already own, on code you keep.

</details>

<details>
<summary><b>How is it different from just using Claude Code or Cursor directly?</b></summary>

A coding agent writes code fast but guesses at what to build and whether it is right. Keel adds the founding-team judgment: what to build, why, in what order, and proof that it works, with a feasibility gate before a line of code.

</details>

<details>
<summary><b>Can Keel build a SaaS app? A mobile app? An MVP?</b></summary>

Yes. Keel is stack-agnostic. The architect chooses and justifies the right technology for your product, whether that is a web app, a SaaS, a mobile app, or an API.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Yes, fully. Use `python tools/run.py check` where docs mention `make`.

</details>

<details>
<summary><b>Are my idea and code private?</b></summary>

Yes. Everything lives in your own git repository on your machine. Keel stores nothing.

</details>

<details>
<summary><b>Do I have to turn my idea into a company?</b></summary>

No. Keel has a **project** mode for when you just want to build something great, a tool, an app, a game, a library, without the market sizing, unit economics, or go-to-market. It skips the business work but keeps the design, the product quality, and the proof that it works.

</details>

<details>
<summary><b>Will it just clone what already exists?</b></summary>

Never, on purpose. Before building, Keel researches what is already out there and holds a hard rule: your idea must be meaningfully better or more original, or it says so and helps you find the angle that makes it new. It will not build you the average version of something that already exists.

</details>

<details>
<summary><b>Can a solo, non-technical founder really ship with this?</b></summary>

That is exactly who it is built for, alongside professional teams. The installer, the guide, and the "tell me the next step" design assume you do not know the commands, and never make you feel like you should.

</details>

---

## Who Keel is for

- **Founders and indie hackers** turning an idea into a fundable, buildable, shippable product.
- **Product managers and designers** who want a spec, a plan, and a build that follows them.
- **Engineers and small teams** who want AI speed without losing quality, ownership, or security.
- **Anyone hitting the wall** with a prompt-to-app tool and needing to reach real production.

---

## Why I built Keel

I'm **Bhargav**, and I have taken a product from an empty folder to real users on my own. Over the past year I shipped an edtech product end to end and largely solo: two mobile apps, a Go backend, a teacher dashboard and an admin console, and the Python content engine behind them, across five languages, taken into a live school pilot with real students. Not a prototype. A deployed product with everything a real one has, and I built every side of it myself: the business case, the product, the design, and the engineering.

Then I did the part almost everyone skips. Before a line of the next version existed, I wrote its specification: a product spec of **180 screens, each with its real states** (loading, empty, error, permission-denied, not just the happy path); **290 build steps put in dependency order** so nothing is ever built before the thing it needs, checked mechanically to **zero ordering violations**; and **every screen traced end to end** to the step that builds it, so nothing gets discovered missing in production. Around half a million words of it. I rebuilt the financial model from prices I checked that day and caught my own earlier numbers understating the true cost to run by **6.7x**.

That is the experience Keel is built from. Not that I can ship, but that I know what a product actually needs, across business, product, and technical, and how much rigor each part deserves. A weekend project should not carry a competitor analysis; a funded startup skipping its unit economics is negligent. A product is not a feature list, it is whether the person you built it for will actually use the thing. Working all of that out end to end, alone, is slow and expensive.

And it taught me where the real difficulty now sits. When AI writes code this fast, building stops being the bottleneck. The hard part, the part that decides whether what you ship is any good, is knowing **what** to build and **why**, for the person you are building it for, and in what order. Every AI tool out there turns a spec into code brilliantly, and every one assumes you already wrote the spec. Most people have not, and the people who need it most are the least sure what a good one contains.

So I built Keel to be the thing I wish I had had: it does that thinking with you, whether you are a seasoned engineer or have never written a line of code, and then it keeps the build honest against it, all the way to production. It carries the product and business judgment I learned the slow, solo way, so you do not have to.

---

## The ideas it is built on

1. **Anything a person must remember is a rule that will eventually be broken.** So a rule must run, be checked, or be short enough to hold.
2. **The AI is the operator, not the instructor.** It never tells you to run a command it can run itself.
3. **Every weakness travels with its fix.** Keel can tell you your idea is weak because it never leaves you there.
4. **Choosing what to build next is a machine's job.** `/next` ranks the candidates and shows the reason.
5. **"Done" is verified, not declared.** `/audit` walks a task against its written definition of done.
6. **"Secure" is proven, not assumed.** `/secure` proves the permission boundary rather than trusting it.
7. **Feasibility is a gate, not a hope.** The business, the product, and the build are audited together before you build on them.

---

<div align="center">

**Give it an idea. Watch it become a plan you can build, and then the product itself.**

Open source (MIT). Star it, use it, contribute.

Built by **[Bhargav](#why-i-built-keel)**, who took a product from idea to real users, solo, end to end, and built Keel so the next person does not have to learn it the slow way.

*AI product builder · idea to production · AI founding team · spec-driven development · works with Claude Code and Cursor*

</div>
