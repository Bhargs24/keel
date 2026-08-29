---
description: Phase 5 - load the build roadmap into the tracker as tasks with dependencies.
argument-hint: [optional milestone to load, e.g. M0]
---

**Phase 5 · Plan - turn the roadmap into a trackable backlog.**

$ARGUMENTS

**Gate check first.** Feasibility must have returned **GO** (see the latest
`docs/50-AUDITS/<date>-feasibility.md`). If it hasn't, stop and run `/feasibility`.

## What to do

Read `spec/03-Technical/BUILD-ROADMAP.md`. For every work item row, create a
tracker task, preserving its ID, milestone, owner (or leave unassigned), and its
dependencies:

```
python tools/track.py add <ID> --title "<what it delivers>" \
  --owner <person or blank> --area <workstream> --milestone <M#> \
  --depends <comma-separated dependency IDs>
```

Do them in dependency order so no `--depends` references a task that doesn't
exist yet. If a row lists a bench it needs first, add that too and wire the
dependency.

If `$ARGUMENTS` names a milestone, load only that milestone (and anything it
depends on). Otherwise load the whole roadmap.

## Verify and report

- Run `python tools/track.py check` - it fails on a dependency that doesn't
  exist or a task ordered ahead of what it needs. Fix any it finds.
- Run `python tools/track.py status` and show it.
- Tell the developer how many tasks were loaded, what the first ready task is,
  and that they can now run `/work` to begin - or `/board` to see the shape.

**From here the build loop takes over:** `/start` to land, `/work` to build,
`/review` and `/audit` and `/test` to verify, `/secure` before anything touching
data ships, `/wrap` to close a session.
