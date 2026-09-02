"""Abstract syntax for the slice of Postgres DDL that governs access control.

We do not parse all of SQL -- only the statements that decide who can see what:
``CREATE TABLE`` (for its columns), ``ALTER TABLE ... ROW LEVEL SECURITY``,
``CREATE POLICY``, and ``GRANT`` / ``REVOKE``. Inside a policy, the ``USING`` and
``WITH CHECK`` clauses are full boolean expressions, so those get a real
expression grammar; everything we do not recognise degrades to
:class:`Unparsed`, which the encoder treats as an opaque (honest-unknown) atom.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
# Expressions (inside USING / WITH CHECK).
# --------------------------------------------------------------------------- #
class Expr:
    """Base class for a policy expression node."""


@dataclass(frozen=True)
class Col(Expr):
    """A column reference, optionally table-qualified (``orders.user_id``)."""

    name: str
    qualifier: str | None = None


@dataclass(frozen=True)
class Literal(Expr):
    value: object  # str | int | float | bool | None
    kind: str  # "str" | "int" | "float" | "bool" | "null"


@dataclass(frozen=True)
class FuncCall(Expr):
    """A function call. ``name`` keeps any schema qualifier, e.g. ``auth.uid``."""

    name: str
    args: tuple[Expr, ...] = ()


@dataclass(frozen=True)
class Binary(Expr):
    op: str  # = <> != < <= > >= and or + - * / etc.
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Unary(Expr):
    op: str  # not, -
    operand: Expr


@dataclass(frozen=True)
class IsNullExpr(Expr):
    operand: Expr
    negated: bool


@dataclass(frozen=True)
class BoolTest(Expr):
    """``operand IS [NOT] TRUE | FALSE | UNKNOWN`` -- Postgres's two-valued
    boolean tests. Unlike ``=``, these never yield NULL, which is exactly why
    policies use them on nullable boolean columns."""

    operand: Expr
    value: str  # "true" | "false" | "unknown"
    negated: bool


@dataclass(frozen=True)
class DistinctFrom(Expr):
    """``left IS [NOT] DISTINCT FROM right`` -- null-safe (two-valued) equality."""

    left: Expr
    right: Expr
    negated: bool  # True for IS NOT DISTINCT FROM


@dataclass(frozen=True)
class InList(Expr):
    operand: Expr
    items: tuple[Expr, ...]
    negated: bool


@dataclass(frozen=True)
class Cast(Expr):
    operand: Expr
    type_name: str


@dataclass(frozen=True)
class JsonAccess(Expr):
    """``base -> key`` or ``base ->> key`` (JSON / JSONB field access)."""

    op: str  # "->" or "->>"
    base: Expr
    key: Expr


@dataclass(frozen=True)
class Unparsed(Expr):
    """A span we chose not to model precisely (a subquery, ``EXISTS``, arithmetic).

    Carrying the original text lets findings explain *why* they are uncertain.
    """

    text: str


# --------------------------------------------------------------------------- #
# Statements.
# --------------------------------------------------------------------------- #
@dataclass
class Column:
    name: str
    type_name: str
    not_null: bool = False

    @property
    def is_bool(self) -> bool:
        return self.type_name.lower() in {"bool", "boolean"}


@dataclass
class CreateTable:
    name: str
    columns: list[Column] = field(default_factory=list)


@dataclass
class AlterRLS:
    table: str
    action: str  # "enable" | "disable" | "force" | "no_force"


@dataclass
class CreatePolicy:
    name: str
    table: str
    permissive: bool = True
    command: str = "all"  # all | select | insert | update | delete
    roles: list[str] | None = None  # None => PUBLIC
    using: Expr | None = None
    check: Expr | None = None


@dataclass
class Grant:
    privileges: list[str]  # upper-case; may contain "ALL"
    table: str
    roles: list[str]
    revoke: bool = False


Statement = CreateTable | AlterRLS | CreatePolicy | Grant
