# The Session Protocol

*Class: **LIVING** · Last-updated: · Owner: <who>. How a working session opens, runs, and closes. The hooks enforce most of this so it isn't left to memory.*

---

## Open

**The developer types `/start`.** The `SessionStart` hook has already printed the branch, the pipeline phase, the claims in `NOW.md`, the tracker state, and what's ready. Claude reads the rulebook, the last two handoffs, and `CLAUDE.md`, then briefs in under twenty lines and **stops** - it proposes the next action and waits.

## Run

**One session, one task.** Context rot is structural, not user error: attention degrades well before the window fills. When a session starts contradicting itself or feeling stupid, it's not being difficult - restart it. The pattern is `/wrap` → `/clear` → `/start`.

- Claude runs the ceremony (claim, branch, log, check), never asking the developer to run a command it can run.
- **Cite the spec, never paraphrase it from memory.** The documentation only pays off if prompts point at `spec/…` instead of describing it.
- **Plan mode before anything above T0** (`CHANGE-PROTOCOL.md`).
- Log to the tracker at every real decision, surprise, or dead end - unprompted.

## Close

The `Stop` hook checks these happened, so they aren't left to memory:

- The honest state is logged (half-done is fine; **half-done and silent is not**).
- The task is moved: `review`, `done`, or `block`.
- The handoff is written to `docs/40-HANDOFF/`, with its *what I know that isn't written anywhere* section - the whole value of the file.
- Every changed file is changelogged; any contradicted document is fixed in the same commit.
- `python tools/run.py check` is green, and the work is committed to a branch (never `main`).

`/wrap` does all of this. Run it before stopping, even for an hour, and **especially before `/clear`.**

## The three habits

- **Plan mode for anything large.** `shift+tab` twice. Claude proposes without touching a file.
- **`/clear` between tasks.** Two clean sessions beat one long, drifting one.
- **Worktrees for two things at once** - separate folder, separate session, same repo, no stashing: `git worktree add ../proj-t001 <person>/<TASK-ID>-<slug>`.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
