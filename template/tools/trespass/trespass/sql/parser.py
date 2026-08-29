"""A focused recursive-descent parser for the access-control DDL fragment.

It reads a whole ``.sql`` file, keeps the four statement kinds that matter
(``CREATE TABLE``, ``ALTER TABLE ... RLS``, ``CREATE POLICY``, ``GRANT`` /
``REVOKE``), and silently skips everything else (indexes, functions, inserts).
Policy ``USING`` / ``WITH CHECK`` clauses are parsed with a real Pratt-style
precedence grammar; any construct we choose not to model -- a subquery, an
``EXISTS``, arithmetic -- is preserved verbatim as :class:`~trespass.sql.ast.Unparsed`
so the analysis can stay honest about what it did and did not understand.
"""

from __future__ import annotations

from .ast import (
    AlterRLS,
    Binary,
    Cast,
    Col,
    Column,
    CreatePolicy,
    CreateTable,
    Expr,
    FuncCall,
    Grant,
    InList,
    IsNullExpr,
    JsonAccess,
    Literal,
    Statement,
    Unary,
    Unparsed,
)
from .lexer import Token, tokenize

_CMP_OPS = {"=", "<>", "!=", "<", "<=", ">", ">="}
_CONSTRAINT_STARTS = {"constraint", "primary", "foreign", "unique", "check", "exclude", "like"}
_COL_CONSTRAINT_KW = {"not", "null", "default", "references", "primary", "unique",
                      "check", "generated", "collate", "constraint"}


class ParseError(ValueError):
    pass


class _Cursor:
    def __init__(self, sql: str, tokens: list[Token]) -> None:
        self.sql = sql
        self.toks = tokens
        self.i = 0

    def peek(self, offset: int = 0) -> Token:
        j = self.i + offset
        return self.toks[j] if j < len(self.toks) else self.toks[-1]

    def next(self) -> Token:
        t = self.peek()
        self.i += 1
        return t

    def at_kw(self, *words: str) -> bool:
        t = self.peek()
        return t.kind == "kw" and t.value.lower() in words

    def at_op(self, *ops: str) -> bool:
        t = self.peek()
        return t.kind == "op" and t.value in ops

    def eat_kw(self, word: str) -> bool:
        if self.at_kw(word):
            self.i += 1
            return True
        return False

    def eat_op(self, op: str) -> bool:
        if self.at_op(op):
            self.i += 1
            return True
        return False

    def expect_op(self, op: str) -> None:
        if not self.eat_op(op):
            raise ParseError(f"expected {op!r}, got {self.peek().value!r} at {self.peek().pos}")


# --------------------------------------------------------------------------- #
# Top level.
# --------------------------------------------------------------------------- #
def parse(sql: str) -> list[Statement]:
    cur = _Cursor(sql, tokenize(sql))
    out: list[Statement] = []
    while cur.peek().kind != "eof":
        start = cur.i
        stmt = _parse_statement(cur)
        if stmt is not None:
            out.append(stmt)
        # Always resync to just past the next top-level ';'.
        _skip_to_semicolon(cur)
        if cur.i == start:  # safety: never spin
            cur.i += 1
    return out


def _skip_to_semicolon(cur: _Cursor) -> None:
    depth = 0
    while cur.peek().kind != "eof":
        if cur.at_op("("):
            depth += 1
        elif cur.at_op(")"):
            depth = max(0, depth - 1)
        elif cur.at_op(";") and depth == 0:
            cur.i += 1
            return
        cur.i += 1


def _parse_statement(cur: _Cursor) -> Statement | None:
    if cur.at_kw("create"):
        if cur.peek(1).kind == "kw" and cur.peek(1).value.lower() == "table":
            return _parse_create_table(cur)
        if cur.peek(1).kind == "kw" and cur.peek(1).value.lower() == "policy":
            return _parse_create_policy(cur)
        return None
    if cur.at_kw("alter") and cur.peek(1).value.lower() == "table":
        return _parse_alter_table(cur)
    if cur.at_kw("grant", "revoke"):
        return _parse_grant(cur)
    return None


# --------------------------------------------------------------------------- #
# Names.
# --------------------------------------------------------------------------- #
def _parse_name(cur: _Cursor) -> tuple[str | None, str]:
    """Parse a possibly-qualified name; return (qualifier, name), lower-cased."""
    parts: list[str] = []
    while cur.peek().kind in {"ident", "kw"}:
        parts.append(cur.next().value.lower())
        if not cur.eat_op("."):
            break
    if not parts:
        raise ParseError(f"expected a name at {cur.peek().pos}")
    if len(parts) == 1:
        return None, parts[0]
    return parts[-2], parts[-1]


def _table_name(cur: _Cursor) -> str:
    cur.eat_kw("if")  # IF NOT EXISTS
    cur.eat_kw("not")
    cur.eat_kw("exists")
    cur.eat_kw("only")
    _, name = _parse_name(cur)
    return name


# --------------------------------------------------------------------------- #
# CREATE TABLE.
# --------------------------------------------------------------------------- #
def _parse_create_table(cur: _Cursor) -> CreateTable | None:
    cur.eat_kw("create")
    cur.eat_kw("table")
    name = _table_name(cur)
    if not cur.eat_op("("):
        return CreateTable(name)  # e.g. CREATE TABLE ... AS / PARTITION OF
    columns: list[Column] = []
    while not cur.at_op(")") and cur.peek().kind != "eof":
        col = _parse_column_entry(cur)
        if col is not None:
            columns.append(col)
        if not cur.eat_op(","):
            break
    cur.eat_op(")")
    return CreateTable(name, columns)


def _parse_column_entry(cur: _Cursor) -> Column | None:
    entry: list[Token] = []
    depth = 0
    while cur.peek().kind != "eof":
        if cur.at_op("(") :
            depth += 1
        elif cur.at_op(")"):
            if depth == 0:
                break
            depth -= 1
        elif cur.at_op(",") and depth == 0:
            break
        entry.append(cur.next())
    if not entry:
        return None
    first = entry[0].value.lower()
    if first in _CONSTRAINT_STARTS:
        return None
    name = first
    type_name = entry[1].value.lower() if len(entry) > 1 else ""
    lowered = [t.value.lower() for t in entry]
    not_null = any(
        lowered[k] == "not" and k + 1 < len(lowered) and lowered[k + 1] == "null"
        for k in range(len(lowered))
    )
    return Column(name=name, type_name=type_name, not_null=not_null)


# --------------------------------------------------------------------------- #
# ALTER TABLE ... ROW LEVEL SECURITY.
# --------------------------------------------------------------------------- #
def _parse_alter_table(cur: _Cursor) -> AlterRLS | None:
    cur.eat_kw("alter")
    cur.eat_kw("table")
    table = _table_name(cur)
    # look for ENABLE/DISABLE/FORCE/NO FORCE ... ROW LEVEL SECURITY
    if cur.eat_kw("enable") and _eat_row_level_security(cur):
        return AlterRLS(table, "enable")
    if cur.eat_kw("disable") and _eat_row_level_security(cur):
        return AlterRLS(table, "disable")
    if cur.eat_kw("force") and _eat_row_level_security(cur):
        return AlterRLS(table, "force")
    if cur.at_kw("no") and cur.peek(1).value.lower() == "force":
        cur.next()
        cur.next()
        if _eat_row_level_security(cur):
            return AlterRLS(table, "no_force")
    return None


def _eat_row_level_security(cur: _Cursor) -> bool:
    return cur.eat_kw("row") and cur.eat_kw("level") and cur.eat_kw("security")


# --------------------------------------------------------------------------- #
# CREATE POLICY.
# --------------------------------------------------------------------------- #
def _parse_create_policy(cur: _Cursor) -> CreatePolicy:
    cur.eat_kw("create")
    cur.eat_kw("policy")
    _, pname = _parse_name(cur)
    if not cur.eat_kw("on"):
        raise ParseError(f"CREATE POLICY without ON at {cur.peek().pos}")
    table = _table_name(cur)
    policy = CreatePolicy(name=pname, table=table)

    if cur.eat_kw("as"):
        if cur.eat_kw("restrictive"):
            policy.permissive = False
        else:
            cur.eat_kw("permissive")
    if cur.eat_kw("for"):
        cmd = cur.next().value.lower()
        policy.command = cmd if cmd in {"all", "select", "insert", "update", "delete"} else "all"
    if cur.eat_kw("to"):
        policy.roles = _parse_role_list(cur)
    if cur.eat_kw("using"):
        cur.expect_op("(")
        policy.using = _parse_expr(cur)
        cur.expect_op(")")
    if cur.eat_kw("with") and cur.eat_kw("check"):
        cur.expect_op("(")
        policy.check = _parse_expr(cur)
        cur.expect_op(")")
    return policy


def _parse_role_list(cur: _Cursor) -> list[str]:
    roles: list[str] = []
    while True:
        t = cur.peek()
        if t.kind in {"ident", "kw"}:
            roles.append(cur.next().value.lower())
        else:
            break
        if not cur.eat_op(","):
            break
    return roles


# --------------------------------------------------------------------------- #
# GRANT / REVOKE.
# --------------------------------------------------------------------------- #
def _parse_grant(cur: _Cursor) -> Grant | None:
    revoke = cur.next().value.lower() == "revoke"
    privileges: list[str] = []
    while cur.peek().kind in {"kw", "ident"} and not cur.at_kw("on"):
        privileges.append(cur.next().value.upper())
        cur.eat_op(",")
    if not cur.eat_kw("on"):
        return None
    cur.eat_kw("table")
    # first table only (GRANT on multiple tables is rare in these schemas)
    table = _table_name(cur)
    while cur.eat_op(","):
        _parse_name(cur)  # ignore additional tables for modelling purposes
    # TO (grant) or FROM (revoke)
    cur.eat_kw("to")
    cur.eat_kw("from")
    roles = _parse_role_list(cur)
    return Grant(privileges=[p for p in privileges if p], table=table, roles=roles, revoke=revoke)


# --------------------------------------------------------------------------- #
# Expression grammar (Pratt-style precedence).
# --------------------------------------------------------------------------- #
def _parse_expr(cur: _Cursor) -> Expr:
    return _parse_or(cur)


def _parse_or(cur: _Cursor) -> Expr:
    left = _parse_and(cur)
    while cur.eat_kw("or"):
        left = Binary("or", left, _parse_and(cur))
    return left


def _parse_and(cur: _Cursor) -> Expr:
    left = _parse_not(cur)
    while cur.eat_kw("and"):
        left = Binary("and", left, _parse_not(cur))
    return left


def _parse_not(cur: _Cursor) -> Expr:
    if cur.eat_kw("not"):
        return Unary("not", _parse_not(cur))
    return _parse_cmp(cur)


def _parse_cmp(cur: _Cursor) -> Expr:
    left = _parse_additive(cur)
    # IS [NOT] NULL / IS [NOT] DISTINCT FROM
    if cur.eat_kw("is"):
        negated = cur.eat_kw("not")
        if cur.eat_kw("null"):
            return IsNullExpr(left, negated)
        if cur.eat_kw("distinct"):
            cur.eat_kw("from")
            right = _parse_additive(cur)
            return Unparsed(_span(cur, left, right, "is distinct from"))
        # IS TRUE / IS FALSE and similar -> opaque
        cur.next()
        return Unparsed("is-predicate")
    # [NOT] IN (...)
    negated_in = False
    if cur.at_kw("not") and cur.peek(1).value.lower() == "in":
        cur.next()
        negated_in = True
    if cur.eat_kw("in"):
        cur.expect_op("(")
        if cur.at_kw("select"):
            return InList(left, (Unparsed(_consume_balanced_from_open(cur)),), negated_in)
        items: list[Expr] = []
        while not cur.at_op(")") and cur.peek().kind != "eof":
            items.append(_parse_expr(cur))
            if not cur.eat_op(","):
                break
        cur.expect_op(")")
        return InList(left, tuple(items), negated_in)
    # binary comparison operators
    if cur.peek().kind == "op" and cur.peek().value in _CMP_OPS:
        op = cur.next().value
        right = _parse_additive(cur)
        return Binary(op, left, right)
    return left


def _parse_additive(cur: _Cursor) -> Expr:
    left = _parse_multiplicative(cur)
    while cur.at_op("+", "-"):
        op = cur.next().value
        left = Binary(op, left, _parse_multiplicative(cur))
    return left


def _parse_multiplicative(cur: _Cursor) -> Expr:
    left = _parse_postfix(cur)
    while cur.at_op("*", "/", "%"):
        op = cur.next().value
        left = Binary(op, left, _parse_postfix(cur))
    return left


def _parse_postfix(cur: _Cursor) -> Expr:
    node = _parse_primary(cur)
    while True:
        if cur.at_op("->", "->>"):
            op = cur.next().value
            node = JsonAccess(op, node, _parse_primary(cur))
        elif cur.eat_op("::"):
            _, type_name = _parse_name(cur)
            # optional (n) or [] on the type
            if cur.eat_op("("):
                _consume_balanced_from_open(cur)
            cur.eat_op("[")
            cur.eat_op("]")
            node = Cast(node, type_name)
        else:
            return node


def _parse_primary(cur: _Cursor) -> Expr:
    t = cur.peek()
    # unary minus
    if cur.at_op("-"):
        cur.next()
        return Unary("-", _parse_primary(cur))
    if cur.eat_op("("):
        if cur.at_kw("select"):
            # rewind one so the balanced consumer sees the '('
            cur.i -= 1
            return Unparsed(_consume_balanced(cur))
        inner = _parse_expr(cur)
        cur.expect_op(")")
        return inner
    if cur.at_kw("exists"):
        cur.next()
        return Unparsed(_consume_balanced(cur))
    if t.kind == "str":
        cur.next()
        return Literal(t.value, "str")
    if t.kind == "num":
        cur.next()
        return _number(t.value)
    if cur.at_kw("null"):
        cur.next()
        return Literal(None, "null")
    if cur.at_kw("true"):
        cur.next()
        return Literal(True, "bool")
    if cur.at_kw("false"):
        cur.next()
        return Literal(False, "bool")
    if t.kind in {"ident", "kw"}:
        qualifier, name = _parse_name(cur)
        full = f"{qualifier}.{name}" if qualifier else name
        if cur.at_op("("):
            args = _parse_arg_list(cur)
            return FuncCall(full, tuple(args))
        return Col(name=name, qualifier=qualifier)
    raise ParseError(f"unexpected {t.value!r} at {t.pos}")


def _parse_arg_list(cur: _Cursor) -> list[Expr]:
    cur.expect_op("(")
    args: list[Expr] = []
    while not cur.at_op(")") and cur.peek().kind != "eof":
        if cur.at_op("*"):
            cur.next()
            args.append(Unparsed("*"))
        else:
            args.append(_parse_expr(cur))
        if not cur.eat_op(","):
            break
    cur.expect_op(")")
    return args


def _number(text: str) -> Literal:
    try:
        if any(c in text for c in ".eE"):
            return Literal(float(text), "float")
        return Literal(int(text), "int")
    except ValueError:
        return Literal(text, "str")


def _consume_balanced(cur: _Cursor) -> str:
    """Consume a balanced ``( ... )`` group starting at the current ``(``; return
    its source text so an unmodeled construct keeps its original wording."""
    open_tok = cur.peek()
    cur.expect_op("(")
    return _consume_balanced_body(cur, open_tok)


def _consume_balanced_from_open(cur: _Cursor) -> str:
    open_tok = cur.toks[cur.i - 1]
    return _consume_balanced_body(cur, open_tok)


def _consume_balanced_body(cur: _Cursor, open_tok: Token) -> str:
    depth = 1
    while cur.peek().kind != "eof" and depth:
        if cur.at_op("("):
            depth += 1
        elif cur.at_op(")"):
            depth -= 1
            if depth == 0:
                close = cur.next()
                return cur.sql[open_tok.pos : close.pos + 1]
        cur.next()
    return cur.sql[open_tok.pos :]


def _span(cur: _Cursor, left: Expr, right: Expr, label: str) -> str:
    return label
