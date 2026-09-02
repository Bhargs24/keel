"""Parser tests: the statement shapes and expression grammar we depend on."""

from __future__ import annotations

from trespass.encode import render_expr
from trespass.schema import build_schema
from trespass.sql import ast
from trespass.sql.parser import parse


def test_create_table_columns_and_not_null() -> None:
    (stmt,) = parse("create table t (id uuid primary key, user_id uuid not null, flag boolean);")
    assert isinstance(stmt, ast.CreateTable)
    cols = {c.name: c for c in stmt.columns}
    assert set(cols) == {"id", "user_id", "flag"}
    assert cols["user_id"].not_null
    assert not cols["id"].not_null
    assert cols["flag"].is_bool


def test_schema_qualified_table_is_normalized() -> None:
    schema = build_schema("create table public.orders (id uuid);")
    assert schema.table("orders") is not None


def test_policy_clauses_are_parsed() -> None:
    (stmt,) = parse(
        "create policy p on t as restrictive for update to authenticated, anon "
        "using (a = 1) with check (b = 2);"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    assert stmt.permissive is False
    assert stmt.command == "update"
    assert stmt.roles == ["authenticated", "anon"]
    assert render_expr(stmt.using) == "a = 1"
    assert render_expr(stmt.check) == "b = 2"


def test_policy_without_to_is_public() -> None:
    (stmt,) = parse("create policy p on t for select using (true);")
    assert isinstance(stmt, ast.CreatePolicy)
    assert stmt.roles is None  # PUBLIC


def test_json_and_cast_expressions() -> None:
    (stmt,) = parse(
        "create policy p on t for select using (org_id = (auth.jwt() ->> 'org_id')::uuid);"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    text = render_expr(stmt.using)
    assert "auth.jwt()" in text and "->>" in text and "org_id" in text


def test_subquery_degrades_to_unparsed() -> None:
    (stmt,) = parse(
        "create policy p on t for select using "
        "(team_id in (select team_id from members where user_id = auth.uid()));"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    # The IN-subquery is preserved verbatim rather than mis-modeled.
    assert isinstance(stmt.using, ast.InList)
    assert isinstance(stmt.using.items[0], ast.Unparsed)
    assert "select" in stmt.using.items[0].text.lower()


def test_grants_and_revokes() -> None:
    schema = build_schema(
        "create table t (id uuid);\n"
        "grant select, insert on t to anon, authenticated;\n"
        "revoke insert on t from anon;"
    )
    assert "insert" not in schema.api_access("t", "insert", assume_default_grants=False) or True
    # With default grants off, only explicit grants count; anon lost insert via revoke.
    anon_insert = "anon" in schema.api_access("t", "insert", assume_default_grants=False)
    assert not anon_insert


def test_unknown_statements_are_skipped() -> None:
    stmts = parse(
        "create extension if not exists pgcrypto;\n"
        "create index idx on t (user_id);\n"
        "create table t (id uuid);\n"
        "insert into t values (gen_random_uuid());"
    )
    tables = [s for s in stmts if isinstance(s, ast.CreateTable)]
    assert len(tables) == 1


def test_comments_are_ignored() -> None:
    stmts = parse(
        "-- a line comment\n"
        "/* a block /* nested */ comment */\n"
        "create table t (id uuid); -- trailing"
    )
    assert len(stmts) == 1


def test_scalar_subselect_resolves_to_its_expression() -> None:
    """`(select auth.uid())` with no FROM clause is just `auth.uid()` -- the
    initplan idiom must produce the real session term, not an opaque blob."""
    (stmt,) = parse(
        "create policy p on t for select using ((select auth.uid()) = user_id);"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    assert isinstance(stmt.using, ast.Binary) and stmt.using.op == "="
    assert isinstance(stmt.using.left, ast.FuncCall)
    assert stmt.using.left.name == "auth.uid"


def test_boolean_tests_and_distinct_from_parse_precisely() -> None:
    (stmt,) = parse(
        "create policy p on t for select using (flag is true and a is distinct from b);"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    assert isinstance(stmt.using, ast.Binary) and stmt.using.op == "and"
    assert isinstance(stmt.using.left, ast.BoolTest)
    assert stmt.using.left.value == "true" and not stmt.using.left.negated
    assert isinstance(stmt.using.right, ast.DistinctFrom)


def test_unknown_operators_parse_as_generic_binaries() -> None:
    """`||`, `@>`, `?` and other unmodeled operators must tokenize and parse
    (the encoder keeps them opaque) instead of aborting the whole file."""
    (stmt,) = parse(
        "create policy p on t for select using (tags @> meta or name || suffix = label);"
    )
    assert isinstance(stmt, ast.CreatePolicy)
    assert stmt.using is not None  # parsed, not crashed


def test_unparseable_clause_degrades_to_opaque_not_a_crash() -> None:
    """A CASE expression is outside the grammar; the clause must survive as one
    opaque span and the rest of the file must still be parsed."""
    stmts = parse(
        "create policy p on t for select using "
        "(case when is_public then true else user_id = auth.uid() end);\n"
        "create table t (id uuid);"
    )
    assert len(stmts) == 2
    policy = stmts[0]
    assert isinstance(policy, ast.CreatePolicy)
    assert isinstance(policy.using, ast.Unparsed)
    assert "case" in policy.using.text.lower()


def test_dollar_parameter_is_not_a_string_start() -> None:
    """`$1` must not be mistaken for a dollar-quote tag and swallow the file."""
    stmts = parse(
        "create policy p on t for select using (current_setting($1) = 'x');\n"
        "create table t (id uuid);"
    )
    tables = [s for s in stmts if isinstance(s, ast.CreateTable)]
    assert len(tables) == 1


def test_non_public_schema_stays_qualified() -> None:
    schema = build_schema(
        "create table auth.users (id uuid);\ncreate table users (id uuid, user_id uuid);"
    )
    assert schema.table("auth.users") is not None
    assert schema.table("users") is not None
    assert schema.table("auth.users") is not schema.table("users")
