# The Arsenal - this project's vetted tooling

*Class: **LIVING** · Last-updated: · Owner: <who>. The open-source tools, skills, MCP servers, and libraries this project uses, each vetted for safety. Maintained by the **tool-scout** via `/equip`. Nothing goes in this list unvetted, and nothing that touches data or credentials goes in without a founder's yes.*

> **Few, not many.** Every MCP server and skill costs the AI focus on every task. The best arsenal is a small, sharp one. When in doubt, leave it out.

---

## Install now
Clear value, safe, low cost.

| Tool | Kind | What it does for us | License | Data reach | Verdict |
|---|---|---|---|---|---|
| | MCP / skill / dev tool / library | | | none / files / network / secrets | safe |

## Consider
Useful, but a trade-off (context cost, maturity, narrow use). Decide per need.

| Tool | Kind | The trade-off | Data reach |
|---|---|---|---|
| | | | |

## Skip (and why)
Recorded so nobody re-litigates it.

| Tool | Why we skipped it |
|---|---|
| | |

---

## The vetting checklist (run for every candidate before it goes in)

- [ ] **What does it actually do?** Read its README and, for anything with access, its source. If you can't tell, do not add it.
- [ ] **What permissions does it need?** File read, command execution, network. Least privilege wins.
- [ ] **Does it reach data or credentials?** If it can see secrets, user data, or the database, it is a **founder-approved** decision, not a default.
- [ ] **Does it phone home?** Any telemetry or outbound calls, and to where.
- [ ] **Is it maintained and used?** Recent commits, real adoption, an open license.
- [ ] **What does it cost the agent?** An MCP server adds tool schemas to context on every task. Is the value worth the focus?

**The rule:** a tool that could touch this project's data or credentials never enters silently. Read it, size its reach, and get an explicit yes.
