# trespass (vendored into Keel)

**Prove your tenants can't read each other's data.** A formal analyzer for
Postgres / Supabase row-level security. It compiles every policy into logic and
either *proves* no user can reach another user's rows, or hands you the exact
query that shows they can.

Broken access control - one user reaching another's data - is the single most
common way AI-built apps leak, and the one class ordinary scanners structurally
miss, because catching it needs to know who is *supposed* to see what. That's the
gap `trespass` is built around: you declare intent, it proves the policy enforces it.

## Run it

Zero dependencies - stdlib only, nothing to install:

```bash
python tools/trespass/run.py check supabase/migrations/
python tools/trespass/run.py check schema.sql --intent app.intent
```

It's wired into `make secure`, `make check`, and the `/secure` command, and it
exits non-zero when a policy leaks, so a broken authorization policy fails the build.

## Verdicts

| Verdict | Meaning |
|---|---|
| **VULNERABLE** | A concrete caller and row that breaks isolation - with the SQL to reproduce it |
| **ISOLATED** | Proved: no such caller exists |
| **UNKNOWN** | A policy leaned on something not modeled precisely (a subquery, an inequality) - reported honestly, never assumed safe |

## Intent

Without configuration it infers ownership from column names (`user_id` looks
owned, `org_id` looks tenant-scoped) and runs conservatively. Declaring intent
turns ambiguity into a hard verdict:

```ini
# app.intent
[documents]
tenant = user_id
select = owner        # only the owner may read
insert = owner
update = owner
delete = owner
```

The gap between declared intent and enforced policy *is* the vulnerability.

---

*This is the maintained copy that ships with Keel. The tool is written from
scratch on the standard library: a purpose-built SMT solver for the row-level
security fragment (equality logic + NULL, three-valued Kleene evaluation),
validated against Z3 and against a real Postgres. `trespass/` holds the source.*
