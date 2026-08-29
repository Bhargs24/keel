"""Dynamic validation: the solver's verdict must match real Postgres RLS.

This is the third leg of the correctness story. The unit tests pin the logic, the
differential test checks the solver against Z3, and this test checks the whole
tool against the actual database: it stands up each policy in a real Postgres,
seeds an attacker row and a victim row, connects as a non-owner role, and asks
Postgres whether the victim's row leaks -- then asserts that trespass predicted
the same thing.

Runs only when ``TRESPASS_PG_DSN`` is set (CI provides a Postgres service).
Skipped otherwise, so the everyday test run stays dependency-free.
"""

from __future__ import annotations

import os
import uuid

import pytest

from trespass.analyze import analyze
from trespass.intent import load_intent
from trespass.schema import build_schema  # noqa: F401  (kept for parity with README)

psycopg = pytest.importorskip("psycopg")
DSN = os.environ.get("TRESPASS_PG_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="TRESPASS_PG_DSN not set")

# A minimal Supabase-compatible shim so real policies run in vanilla Postgres.
_PRELUDE = """
create schema if not exists auth;
create or replace function auth.uid() returns uuid language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
create or replace function auth.role() returns text language sql stable as $$
  select coalesce(nullif(current_setting('request.jwt.claim.role', true), ''), 'anon') $$;
create or replace function auth.jwt() returns jsonb language sql stable as $$
  select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb) $$;
do $$ begin
  if not exists (select from pg_roles where rolname = 'app_user') then
    create role app_user nologin;
  end if;
end $$;
"""

# (policy USING clause, intent access level, expected: does the victim row leak?)
_CASES = [
    ("true", "owner", True),
    ("user_id = auth.uid()", "owner", False),
    ("user_id = auth.uid() or is_public", "owner", True),
    ("user_id = auth.uid() or user_id is null", "owner", False),
]


@pytest.fixture(scope="module")
def conn():  # type: ignore[no-untyped-def]
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute(_PRELUDE)
        yield c


@pytest.mark.parametrize("using,level,expect_leak", _CASES, ids=[c[0] for c in _CASES])
def test_solver_matches_postgres(conn, using: str, level: str, expect_leak: bool) -> None:  # type: ignore[no-untyped-def]
    attacker, victim = uuid.uuid4(), uuid.uuid4()
    table = "t_" + uuid.uuid4().hex[:8]

    schema_sql = (
        f"create table {table} (id uuid primary key default gen_random_uuid(), "
        f"user_id uuid not null, is_public boolean default false);\n"
        f"alter table {table} enable row level security;\n"
        f"alter table {table} force row level security;\n"
        f"create policy p on {table} for select to app_user using ({using});"
    )
    conn.execute(schema_sql)
    conn.execute(f"grant select on {table} to app_user;")
    conn.execute(
        f"insert into {table} (user_id, is_public) values (%s, false), (%s, true);",
        (attacker, victim),
    )

    # --- ground truth: what does Postgres actually allow the attacker to read? ---
    with conn.cursor() as cur:
        cur.execute("set role app_user;")
        cur.execute("select set_config('request.jwt.claim.sub', %s, false);", (str(attacker),))
        cur.execute("select set_config('request.jwt.claim.role', 'authenticated', false);")
        cur.execute(f"select count(*) from {table} where user_id = %s;", (victim,))
        leaked = cur.fetchone()[0] > 0
        cur.execute("reset role;")

    assert leaked is expect_leak, f"Postgres disagreed with the test's own expectation for {using!r}"

    # --- trespass's prediction on the same policy, with a declared owner intent ---
    intent_sql = f"[{table}]\ntenant = user_id\nselect = {level}\n"
    intent_path = f"/tmp/{table}.intent"
    with open(intent_path, "w", encoding="utf-8") as fh:
        fh.write(intent_sql)
    report = analyze(schema_sql, load_intent(intent_path))
    predicted_leak = bool(report.vulnerabilities)

    assert predicted_leak is leaked, (
        f"trespass predicted leak={predicted_leak} but Postgres leak={leaked} for {using!r}"
    )
