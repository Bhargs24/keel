# The Guide: getting the most out of Keel without losing quality

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. How to move fast here without the speed costing you correctness.*

**The thesis: speed and quality do not trade off here.** The same practices that make Keel fast (a spec that already exists, a plan reviewed before code, gates that verify without you re-reading every line, specialists with a clean context) are the ones that keep it right. What destroys quality is skipping them to *feel* faster. This guide is the five-part reference for doing it well.

## The five documents

| # | Read | Covers |
|---|---|---|
| 1 | [CAPABILITIES](1-CAPABILITIES.md) | what your AI tool can do inside Keel, the seven capabilities Keel adds, and the clean split between the machine's job and yours |
| 2 | [WORKFLOWS](2-WORKFLOWS.md) | the plays: running the pipeline (`/keel` to `/plan`) and the build loop (`/start` `/next` `/work` `/review` `/audit` `/test` `/secure` `/ship` `/wrap`), the returning-user flow, company vs project mode |
| 3 | [PROMPTING](3-PROMPTING.md) | how to talk to it: the one-question-at-a-time law, how to give it a good idea, the build-prompt anatomy, the templates, when to push back, how to correct it |
| 4 | [ARSENAL](4-ARSENAL.md) | getting the most from `/equip` and the tool-scout, safely. The vetted list itself lives in [ARSENAL.md](ARSENAL.md) |
| 5 | [SETUP](5-SETUP.md) | install with any AI tool, the guide cockpit (`python tools/keel.py`), the tracker, and the gates |

## The five things that matter most

1. **Point at the spec, never describe it.** Keel's whole front half exists so that when you build, you cite `spec/…` instead of paraphrasing from memory. Adjacent is the expensive failure.
2. **Let the gate do its job.** When `/feasibility` says REVISE, fix the plan first. When `/audit` says a task is not done, it is not. When `/secure` finds a hole, it is a hole. The gates are cheap; the bug they catch after launch is not.
3. **One session, one task.** Context rot is structural, not user error. When a session starts contradicting itself, restart it: `/wrap`, `/clear`, `/start`.
4. **Plan mode before anything large.** Pour the effort into the plan so the build is one shot. If it goes wrong mid-implementation, re-plan rather than steer.
5. **Approve, do not administrate.** Keel runs the ceremony. Your leverage is in the decisions it surfaces (the wedge, the trade-off, the thing with no undo), not in remembering commands.

## The enforcement layer (why you do not have to remember)

Rules that depend on being remembered fail under deadline. These do not:

| Mechanism | Enforces |
|---|---|
| `UserPromptSubmit` hook | the rule preamble, on **every single prompt** |
| `PreToolUse` hook | blocks a write that carries a secret |
| `PostToolUse` hook | format and lint on every edit |
| `Stop` hook | the tracker updated, the handoff written, nothing left uncommitted |
| `no_placeholders` in CI | no TODO, stub, mock, or "for now" reaches the main branch |
| `dep_check` in CI | module boundaries, so the codebase cannot rot into a monolith |
| `ownership_check` in CI | who may touch what, so two sessions never quietly overwrite each other |
| `trespass` in CI | a policy that lets one user read another's data fails the build |

## A note on the tools you add

Skills, plugins, and MCP servers can read files, run commands, and send data outward. If your product holds user data, this matters. Nothing third-party goes in without reading what it does, and anything that could touch user data or credentials is a deliberate, owner-approved choice. `/equip` and the tool-scout do this vetting for you; the details are in [ARSENAL](4-ARSENAL.md).
