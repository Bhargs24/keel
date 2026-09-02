# Changelog

All notable changes to keel-kit. The format follows [Keep a Changelog](https://keepachangelog.com/);
versions follow [SemVer](https://semver.org/).

## 0.2.0 — 2026-09-02

The honesty release: every claim the kit makes is now enforced by a test or
removed. 42 tests and CI now cover keel's own code (previously untested).

### Fixed
- **`keel init` gives the project to you, not to a stranger.** The template's
  example roster ("Alex"/"Sam") was shipped as the live roster and `--name` was
  dead code, so the first tracker command failed with "cannot tell who you
  are". The roster is now generated from `--name` or your git identity, the
  template ships only `people.example.toml`, and a one-person roster always
  resolves to that person.
- **The vendored trespass copy was stale and unsound.** It shipped v0.1.0,
  which could print "proved isolated" over a leaking policy. Now pinned to
  v0.2.0 via `scripts/vendor_trespass.py`, recorded in `VENDORED.md` with its
  upstream commit and license, byte-identical to upstream, with a test that
  fails if the pin and the code ever disagree — and a regression test that
  keeps the false proof dead.
- **The gate runner no longer says "passed" for checks that checked nothing.**
  Unarmed gates are reported as `inactive`, each with the reason and the step
  that arms it.
- **`/scaffold` joined the guided journey.** The cockpit and the phase
  detector now surface it between `/plan` and `/work`; previously the guided
  path skipped it, leaving every code gate a stub forever.
- **A fresh project starts at the beginning.** The template's own README stubs
  made phase detection skip the `/keel "your idea"` step.
- **Hooks are cross-platform for real.** All Claude Code hooks are now
  stdlib Python (no `bash`, `cat`, `sed`, `date`), survive legacy Windows
  code pages, and the secret scanner now scans the *incoming* write and blocks
  with exit 2 (the code that actually blocks) instead of scanning the previous
  diff with a non-blocking exit.
- The `WORK-ITEM:` escape hatch now accepts the tracker's own ID format
  (`T-042`, `API-004`).
- The board's write API refuses cross-origin requests.
- The pre-push hook no longer prints a literal `$protected`.
- Timestamps use the machine's local timezone (override with `TRACK_TZ`);
  the board/CLI title comes from `NOW.md`'s `Project:` line or the folder name.
- Removed every remnant of the author's previous project from the template
  (hardcoded app paths, foreign task IDs, domain-specific examples).

### Added
- Test suite for keel's own code (init, tracker, gates, cockpit, hooks,
  vendor pin) and a CI workflow that runs it plus the vendored trespass suite
  (including its Z3 differential tests) on Python 3.10–3.13.
- `template/.gitattributes` so scaffolded projects normalize line endings.
- CHANGELOG, CONTRIBUTING, SECURITY policy, and issue templates.

## 0.1.0 — 2026-08-30

Initial release: the pipeline commands, the specialist agents, the tracker,
the board, the cockpit, the quality gates, and the vendored trespass prover.
