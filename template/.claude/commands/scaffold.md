---
description: Turn the architect's plan into a real, buildable, enforced repo, the directory skeleton, the boundary config, the Makefile commands, and the ownership map, all wired to the chosen stack. Run once, after Feasibility says GO, before the first build.
argument-hint: (none)
---

**Phase 5.5 · Scaffold - make the plan buildable and the gates real.**

The architect chose a stack and a layout (`spec/03-Technical/TECH-STACK.md`,
`DATA-MODEL.md`, `BUILD-ROADMAP.md`). Nothing has wired that into the repo yet:
the boundary gate has no config, the `Makefile`'s lint, typecheck, and test
targets are empty stubs, and the ownership map is a placeholder. Until this runs,
the build lands in a repo where the language-level gates do nothing.

**This step wires all of it, once**, so every task the build produces is checked
against the real stack, not a placeholder. Run it after `/feasibility` returns GO
and before the first `/work`.

## Gate check

`spec/03-Technical/TECH-STACK.md` must exist. If it does not, run `/architect`
first. Read it, `DATA-MODEL.md`, and `BUILD-ROADMAP.md` for the stack, the module
layout, and where the database schema will live.

## What to wire

**1. The directory skeleton.** Create the top-level module directories the
architecture calls for. That might be `apps/`, `services/`, `packages/`; or a
single app with `src/` and `tests/`; or a library layout, whatever the stack and
the build roadmap imply. Only the skeleton and a one-line README per module. No
feature code; that is the build's job.

**2. `tools/boundaries.json`** (the boundary gate). Write it for the chosen
layout, copying the shape from `tools/boundaries.example.json`: the import prefix
(Go module path, npm scope, Dart package prefix, or empty), the layers and what
each may import, sibling isolation, and any generated or leaf modules. If the
project is a single app with no internal module boundaries, say so plainly and
leave `boundaries.json` out; the gate then correctly enforces nothing.

**3. The `Makefile` targets** (the quality gates CI runs). Replace the `lint`,
`typecheck`, `test`, and `gen` stubs with the chosen stack's real commands, each
guarded so a language that is not present is skipped. For example:
- Python: `ruff check .` / `mypy .` / `pytest`
- TypeScript: `eslint .` / `tsc --noEmit` / `vitest run`
- Go: `go vet ./... && staticcheck ./...` / (the compiler is the typecheck) / `go test ./...`
- `gen`: the real generator if the data model drives one (types from the schema,
  clients from a contract), else leave it a no-op.
These are what `.github/workflows/quality.yml` runs; make them real.

**4. `docs/20-WORK/OWNERSHIP.map`.** Set the real paths from the skeleton, mapped
to the real people in `tracker/people.toml`. Generated directories to `GENERATED`,
shared to `SHARED`, each owned area to its owner.

## Verify, do not assume

- `python tools/run.py check` - the cross-stack gates (no placeholders,
  boundaries, ownership, tracker, trespass) must pass on the empty skeleton. If
  one errors, the wiring is wrong. Fix it here, not three tasks into the build.
- `python tools/run.py verify` - confirm the `Makefile` targets actually execute
  for the languages present (an empty skeleton lints and tests to zero findings,
  which is the point: the pipeline runs green from the first commit).

## Finish

A short, plain recap (2 to 4 lines): the layout you created, the stack the gates
now enforce, and the single next step: `/plan` if tasks are not loaded yet, then
`/work` to build the first one. The repo is now one where "production-grade,
tested, enforced" is true of the code, not just the documents.
