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
