---
description: Phase 8 — the production-readiness gate. Walk the checklist, then deploy. Refuses to ship on an unproven boundary or a red gate.
argument-hint: [optional environment, e.g. staging | production]
---

**Getting to production is a gate, not a vibe.** Walk it honestly. A demo that
works is not a product that ships.

## The readiness checklist

Go through each, and for each say **holds / does not hold / cannot verify** with
evidence — never a bare tick.

**Correctness & completeness**
- [ ] The milestone's exit criteria (in `BUILD-ROADMAP.md`) are met, audited with
      `/audit`, not self-reported.
- [ ] `make verify` is green — the fast gates plus lint, types, and tests.
- [ ] No placeholder code, no TODOs, no mocks in the path being shipped.

**Security & data** (run `/secure` and read it)
- [ ] `trespass` proves tenant isolation — no VULNERABLE verdicts on the schema.
- [ ] Authorization enforced server-side; no secrets in the build or client.
- [ ] Every user-facing state handles failure: timeout, partial write, offline.

**Operability**
- [ ] Errors are typed, coded, and logged with a trace id — and **no PII in logs**.
- [ ] There's a way to see it's healthy (a health check, basic metrics) and a way
      to see it broke (error tracking).
- [ ] A rollback path exists and has been thought through, not assumed.
- [ ] Backups / data durability for anything with no undo.
- [ ] Secrets come from a manager, not the repo; the environment is configured.

**The business is ready for the software**
- [ ] The accounts and services in `TOOLS-AND-ACCOUNTS.md` are provisioned.
- [ ] The cost-to-run at launch scale matches `spec/05-Finance/COST-TO-RUN.md`.

## The rule

**A red gate or an unproven boundary does not ship, however urgent.** If
something can't be verified, that's a `cannot verify` on the checklist and a
reason to pause, not to hope. If a check legitimately doesn't apply, say why.

## Then ship

Only when the checklist holds: run the project's deploy path, confirm the health
check, watch the first errors, and record what shipped in `docs/30-CHANGELOG/`.
Report what went out, to where, and what to watch for the first hour.
