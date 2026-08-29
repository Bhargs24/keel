---
description: Phase 7 — prove the permission and data boundaries. Run trespass on the schema, then a security review of the rest.
argument-hint: [optional path to schema/migrations; defaults to auto-detect]
---

**Prove the boundary, don't assert it.** For anything touching auth, money, or
multi-tenant data, "it should be fine" is not a result — either it's proved
isolated, or here is the exact request that breaks it.

## 1 · Prove tenant isolation (the provable part)

Find the database schema — a `schema.sql`, a `supabase/migrations/` directory, or
wherever the data model lives ($ARGUMENTS overrides). Then run the vendored
analyzer yourself:

```
python tools/trespass/run.py check <schema-or-migrations> --intent <intent file if present> --no-color
```

- Read every finding. A **VULNERABLE** verdict is a hole *with a reproduction* —
  treat it as a ship blocker and show the exact query.
- An **UNKNOWN** verdict is the analyzer being honest about a policy it couldn't
  fully model. Read it and judge it by hand; never assume it's safe.
- If there's no intent file, the analysis infers ownership from column names and
  is conservative. For a hard verdict on the ambiguous cases, write the intent
  file (`tools/trespass/README.md` has the format) and re-run.

## 2 · Review the rest (the judgement part)

Use the **security-auditor** subagent for what isn't mechanically provable:
authorization enforced server-side (not just hidden in the UI), no secrets in the
diff or the client bundle, validation on hostile input at the boundary, no
endpoint returning more than the caller should see, no PII in logs, and the
permission invariants in `CLAUDE.md`.

## Report

Lead with the proof: what `trespass` proved isolated, and every VULNERABLE with
its reproduction query. Then the reviewed findings, grouped **must fix before
ship / should fix / worth knowing**, each with the file and the concrete attack
it enables. If the boundaries hold, say what you **proved** versus what you
**reviewed by eye** — the distinction is the whole point.
