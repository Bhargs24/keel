"""The resolved schema: tables, their RLS state, policies, and grants.

This folds the flat list of parsed statements into the model the analyzer
reasons about, resolving the order-dependent bits along the way (an ``ALTER
TABLE ... DISABLE`` after an ``ENABLE`` wins; a later ``FORCE`` sticks).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .sql import ast
from .sql.parser import parse

# Roles PostgREST exposes to the internet in a standard Supabase project.
API_ROLES = ("anon", "authenticated")
_ALL_COMMANDS = ("select", "insert", "update", "delete")


@dataclass
class Policy:
    name: str
    permissive: bool
    command: str
    roles: list[str] | None  # None => PUBLIC (every role)
    using: ast.Expr | None
    check: ast.Expr | None

    def applies_to(self, command: str, role: str) -> bool:
        if self.command != "all" and self.command != command:
            return False
        if self.roles is None:
            return True
        return role in self.roles or "public" in self.roles


@dataclass
class Grant:
    privileges: set[str]  # normalized command names, or {"all"}
    role: str
    revoke: bool


@dataclass
class Table:
    name: str
    columns: dict[str, ast.Column] = field(default_factory=dict)
    rls_enabled: bool = False
    rls_forced: bool = False
    policies: list[Policy] = field(default_factory=list)

    def has_column(self, name: str) -> bool:
        return name.lower() in self.columns

    def column(self, name: str) -> ast.Column | None:
        return self.columns.get(name.lower())


@dataclass
class Schema:
    tables: dict[str, Table] = field(default_factory=dict)
    grants: list[tuple[str, Grant]] = field(default_factory=list)  # (table, grant)

    def table(self, name: str) -> Table | None:
        return self.tables.get(name.lower())

    # ------------------------------------------------------------------ #
    def api_access(
        self, table: str, command: str, *, assume_default_grants: bool = True
    ) -> set[str]:
        """Which internet-facing roles can issue ``command`` against ``table``.

        Supabase grants the ``anon`` and ``authenticated`` roles broad table
        privileges by default and PostgREST exposes the ``public`` schema, so the
        realistic default is "both roles can reach everything" until a ``REVOKE``
        says otherwise. That default is exactly why missing RLS is catastrophic;
        turning it off (``assume_default_grants=False``) makes the analysis rely
        only on grants written in the file.
        """
        allowed: set[str] = set(API_ROLES) if assume_default_grants else set()
        for tname, g in self.grants:
            if tname != table or g.role not in API_ROLES:
                if g.role in ("public",) and tname == table:
                    pass  # public applies to api roles too; handled below
                else:
                    continue
            roles = set(API_ROLES) if g.role == "public" else {g.role}
            covers = command in g.privileges or "all" in g.privileges
            if not covers:
                continue
            if g.revoke:
                allowed -= roles
            else:
                allowed |= roles
        return allowed


def build_schema(sql: str) -> Schema:
    return schema_from_statements(parse(sql))


def schema_from_statements(statements: list[ast.Statement]) -> Schema:
    schema = Schema()
    for st in statements:
        if isinstance(st, ast.CreateTable):
            table = schema.tables.setdefault(st.name, Table(st.name))
            for col in st.columns:
                table.columns[col.name] = col
        elif isinstance(st, ast.AlterRLS):
            table = schema.tables.setdefault(st.table, Table(st.table))
            if st.action == "enable":
                table.rls_enabled = True
            elif st.action == "disable":
                table.rls_enabled = False
            elif st.action == "force":
                table.rls_forced = True
            elif st.action == "no_force":
                table.rls_forced = False
        elif isinstance(st, ast.CreatePolicy):
            table = schema.tables.setdefault(st.table, Table(st.table))
            table.policies.append(
                Policy(
                    name=st.name,
                    permissive=st.permissive,
                    command=st.command,
                    roles=st.roles,
                    using=st.using,
                    check=st.check,
                )
            )
        elif isinstance(st, ast.Grant):
            privs = {p.lower() for p in st.privileges}
            norm: set[str] = set()
            for p in privs:
                if p == "all":
                    norm.add("all")
                elif p in _ALL_COMMANDS:
                    norm.add(p)
            for role in st.roles:
                schema.grants.append(
                    (st.table, Grant(privileges=norm or {"all"}, role=role, revoke=st.revoke))
                )
    return schema
