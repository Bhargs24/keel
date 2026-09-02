"""Analyzer-level regressions: each of these pins a verdict that was once wrong.

The theme is the tool's core promise, in both directions: a VULNERABLE verdict
must describe a reproducible leak, and an ISOLATED verdict must be a real proof.
Every test here started life as a counterexample to one of those claims.
"""

from __future__ import annotations

from trespass.analyze import analyze
from trespass.findings import Verdict
from trespass.intent import Intent, TableIntent


def _owner_intent(table: str, tenant: str = "user_id") -> Intent:
    return Intent(
        tables={table: TableIntent(tenant=tenant, access={"select": "owner"})},
        source="declared",
    )


# --------------------------------------------------------------------------- #
# The initplan idiom: (select auth.uid()) must resolve to the session term.
# --------------------------------------------------------------------------- #
def test_supabase_initplan_idiom_is_isolated() -> None:
    """`(select auth.uid()) = user_id` is the pattern Supabase's own docs
    recommend for performance. It used to degrade to an opaque unknown and
    produce a false CRITICAL; it must prove isolated."""
    sql = (
        "create table documents (id uuid primary key, user_id uuid not null);\n"
        "alter table documents enable row level security;\n"
        "create policy owner_read on documents for select\n"
        "  to authenticated using ((select auth.uid()) = user_id);"
    )
    report = analyze(sql, _owner_intent("documents"))
    assert not report.vulnerabilities, [f.title for f in report.vulnerabilities]
    assert any(f.verdict is Verdict.ISOLATED for f in report.findings)


def test_real_subquery_still_degrades_honestly() -> None:
    """A subselect with a FROM clause is a real subquery; it must stay opaque
    (UNKNOWN at worst), never silently pass and never claim a proof."""
    sql = (
        "create table documents (id uuid primary key, user_id uuid not null);\n"
        "alter table documents enable row level security;\n"
        "create policy team_read on documents for select to authenticated\n"
        "  using (user_id = (select owner_id from teams limit 1));"
    )
    report = analyze(sql, _owner_intent("documents"))
    assert not report.vulnerabilities
    assert not any(f.verdict is Verdict.ISOLATED for f in report.findings)
    assert any(f.verdict is Verdict.UNKNOWN for f in report.findings)


# --------------------------------------------------------------------------- #
# Boolean tests: IS TRUE / IS FALSE must be modeled, and never share an atom.
# --------------------------------------------------------------------------- #
def test_is_true_leak_is_flagged() -> None:
    """`user_id = auth.uid() or (is_public is true and not (deleted is true))`
    leaks public rows to non-owners. The two IS TRUE tests once collapsed into
    a single opaque atom, making the OR branch unsatisfiable -- and the leak was
    reported as a *proof of isolation*."""
    sql = (
        "create table posts (id uuid primary key, user_id uuid not null,\n"
        "  is_public boolean, deleted boolean);\n"
        "alter table posts enable row level security;\n"
        "create policy read on posts for select to authenticated\n"
        "  using (user_id = auth.uid() or (is_public is true and not (deleted is true)));"
    )
    report = analyze(sql, _owner_intent("posts"))
    assert report.vulnerabilities, "the public-read branch must be flagged"
    assert not any(f.verdict is Verdict.ISOLATED for f in report.findings)


def test_distinct_predicates_never_share_an_atom() -> None:
    """Two different IS DISTINCT FROM tests are two different predicates. This
    policy is satisfiable for any caller (a <> b while c = d), so under an
    owner-only intent it must be flagged -- not 'proved' isolated via X AND NOT X."""
    sql = (
        "create table notes (id uuid primary key, user_id uuid not null,\n"
        "  a text, b text, c text, d text);\n"
        "alter table notes enable row level security;\n"
        "create policy weird on notes for select to authenticated\n"
        "  using ((a is distinct from b) and not (c is distinct from d));"
    )
    report = analyze(sql, _owner_intent("notes"))
    assert report.vulnerabilities
    assert not any(f.verdict is Verdict.ISOLATED for f in report.findings)


def test_not_distinct_owner_policy_is_isolated() -> None:
    """IS NOT DISTINCT FROM is null-safe equality; on a NOT NULL tenant column
    it is exactly the owner check and must prove isolated."""
    sql = (
        "create table docs (id uuid primary key, user_id uuid not null);\n"
        "alter table docs enable row level security;\n"
        "create policy own on docs for select to authenticated\n"
        "  using (user_id is not distinct from auth.uid());"
    )
    report = analyze(sql, _owner_intent("docs"))
    assert not report.vulnerabilities
    assert any(f.verdict is Verdict.ISOLATED for f in report.findings)


# --------------------------------------------------------------------------- #
# Witnesses must not rest on unprovable assumptions.
# --------------------------------------------------------------------------- #
def test_opaque_predicate_witness_is_unknown_not_vulnerable() -> None:
    """A CASE expression is kept opaque. A policy that is actually owner-only
    inside a CASE must not be called VULNERABLE on the assumption the opaque
    predicate can be true for an attacker -- the honest verdict is UNKNOWN."""
    sql = (
        "create table t (id uuid primary key, user_id uuid not null);\n"
        "alter table t enable row level security;\n"
        "create policy p on t for select to authenticated\n"
        "  using (case when user_id = auth.uid() then true else false end);"
    )
    report = analyze(sql, _owner_intent("t"))
    assert not report.vulnerabilities
    assert any(f.verdict is Verdict.UNKNOWN for f in report.findings)


def test_column_flag_witness_stays_vulnerable() -> None:
    """A boolean column set to true is a row that can really exist -- the
    canonical `or is_public` hole keeps its hard verdict under declared intent."""
    sql = (
        "create table docs (id uuid primary key, user_id uuid not null, is_public boolean);\n"
        "alter table docs enable row level security;\n"
        "create policy read on docs for select to authenticated\n"
        "  using (user_id = auth.uid() or is_public);"
    )
    report = analyze(sql, _owner_intent("docs"))
    assert report.vulnerabilities
    assert report.vulnerabilities[0].witness is not None
    assert report.vulnerabilities[0].witness.precondition is not None


# --------------------------------------------------------------------------- #
# Real-world files must not kill the run.
# --------------------------------------------------------------------------- #
def test_common_operators_do_not_abort_the_analysis() -> None:
    """`||`, `@>`, and friends appear all over real migrations (generated
    columns, views, defaults). One of them anywhere used to abort the entire
    analysis with a lex error."""
    sql = (
        "create table profiles (id uuid primary key, user_id uuid not null,\n"
        "  full_name text,\n"
        "  search tsvector generated always as (to_tsvector('english', full_name || '')) stored);\n"
        "alter table profiles enable row level security;\n"
        "create policy own on profiles for select to authenticated using (user_id = auth.uid());\n"
        "create view v as select full_name || ' x' from profiles;\n"
        "create table tagged (id uuid primary key, user_id uuid not null, tags jsonb);\n"
        "alter table tagged enable row level security;\n"
        "create policy tags_own on tagged for select to authenticated\n"
        "  using (user_id = auth.uid() and tags @> '{}');"
    )
    report = analyze(sql, _owner_intent("profiles"))
    assert report.tables_analyzed == 2
    assert not report.vulnerabilities
    assert any(f.verdict is Verdict.ISOLATED and f.table == "profiles" for f in report.findings)


# --------------------------------------------------------------------------- #
# Declared intent must line up with the schema, loudly.
# --------------------------------------------------------------------------- #
def test_intent_with_unknown_tenant_column_warns() -> None:
    """A typo'd tenant column used to silently skip every isolation check and
    report a clean run. It must surface as an UNKNOWN finding."""
    sql = (
        "create table posts (id uuid primary key, user_id uuid not null);\n"
        "alter table posts enable row level security;\n"
        "create policy p on posts for select to authenticated using (true);"
    )
    report = analyze(sql, _owner_intent("posts", tenant="usr_id"))
    assert any(f.rule == "intent-unknown-column" for f in report.findings)


def test_intent_with_unknown_table_warns() -> None:
    sql = "create table posts (id uuid primary key, user_id uuid not null);"
    report = analyze(sql, _owner_intent("postz"))
    assert any(f.rule == "intent-unknown-table" for f in report.findings)


# --------------------------------------------------------------------------- #
# Non-public schemas are not internet-reachable by default.
# --------------------------------------------------------------------------- #
def test_non_public_schema_is_not_assumed_reachable() -> None:
    """PostgREST exposes only the `public` schema by default; an internal table
    without RLS is not a finding unless something grants access to it."""
    sql = "create table audit.log (id uuid primary key, actor uuid);"
    report = analyze(sql)
    assert not report.vulnerabilities

    granted = sql + "\ngrant select on audit.log to anon;"
    report = analyze(granted)
    assert any(f.rule == "rls-disabled" for f in report.vulnerabilities)


def test_public_qualifier_is_the_same_table() -> None:
    sql = (
        "create table public.docs (id uuid primary key, user_id uuid not null);\n"
        "alter table docs enable row level security;\n"
        "create policy p on public.docs for select to authenticated using (user_id = auth.uid());"
    )
    report = analyze(sql, _owner_intent("docs"))
    assert report.tables_analyzed == 1
    assert not report.vulnerabilities
    assert any(f.verdict is Verdict.ISOLATED for f in report.findings)
