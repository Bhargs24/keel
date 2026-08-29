"""Translate a parsed policy expression into a three-valued SMT formula.

This is where Postgres semantics meet the solver. Two ideas do the work:

* **Canonical session terms.** ``auth.uid()`` always becomes the same symbolic
  value, ``auth.jwt() ->> 'org_id'`` always becomes the same claim term, and so
  on -- so a policy that compares a column to the caller's identity produces an
  equality the solver can reason about across the whole schema.

* **Honest opacity.** Anything we cannot model precisely -- a subquery, a ``<``
  comparison, an arbitrary boolean function -- becomes an :class:`Opaque` atom.
  Findings that depend on one are reported as UNKNOWN, never as a false proof.
"""

from __future__ import annotations

from .smt import (
    FALSE,
    NULL,
    TRUE,
    Eq,
    Formula,
    Func,
    IsNull,
    Opaque,
    Term,
    Var,
    and_,
    not_,
    or_,
)
from .sql import ast

#: The authenticated caller's identity. Null exactly when the caller is anonymous.
SESSION_UID: Var = Var("auth.uid()")
#: The caller's Postgres role name (``anon`` / ``authenticated`` / ...).
SESSION_ROLE: Var = Var("auth.role()")


class Encoder:
    def __init__(self, table: str) -> None:
        self.table = table

    # -- boolean position -------------------------------------------------- #
    def formula(self, e: ast.Expr) -> Formula:
        if isinstance(e, ast.Binary):
            if e.op == "and":
                return and_(self.formula(e.left), self.formula(e.right))
            if e.op == "or":
                return or_(self.formula(e.left), self.formula(e.right))
            if e.op == "=":
                return Eq(self.term(e.left), self.term(e.right))
            if e.op in ("<>", "!="):
                return not_(Eq(self.term(e.left), self.term(e.right)))
            return Opaque(f"cmp:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.Unary):
            if e.op == "not":
                return not_(self.formula(e.operand))
            return Opaque(f"un:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.IsNullExpr):
            f: Formula = IsNull(self.term(e.operand))
            return not_(f) if e.negated else f
        if isinstance(e, ast.InList):
            eqs = [Eq(self.term(e.operand), self.term(it)) for it in e.items]
            base: Formula = or_(*eqs) if eqs else FALSE
            return not_(base) if e.negated else base
        if isinstance(e, ast.Literal):
            if e.kind == "bool":
                return TRUE if e.value else FALSE
            if e.kind == "null":
                return Eq(NULL, NULL)  # a formula that is always NULL
            return Opaque(f"lit:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.Col):
            return Opaque(f"col:{self._cname(e)}", nullable=True)
        if isinstance(e, ast.Cast):
            if e.type_name.lower() in ("bool", "boolean"):
                return self.formula(e.operand)
            return Opaque(f"cast:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.FuncCall):
            return Opaque(f"pred:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.JsonAccess):
            return Opaque(f"json:{expr_key(e)}", nullable=True)
        if isinstance(e, ast.Unparsed):
            return Opaque(f"raw:{e.text}", nullable=True)
        return Opaque(f"expr:{expr_key(e)}", nullable=True)

    # -- value position ---------------------------------------------------- #
    def term(self, e: ast.Expr) -> Term:
        if isinstance(e, ast.Col):
            return Var(self._cname(e))
        if isinstance(e, ast.Literal):
            return NULL if e.kind == "null" else _lit(e.value)
        if isinstance(e, ast.FuncCall):
            name = e.name.lower()
            if name in ("auth.uid", "uid"):
                return SESSION_UID
            if name in ("auth.role", "role"):
                return SESSION_ROLE
            if name == "current_setting":
                key = self.term(e.args[0]) if e.args else _lit("")
                return Func("current_setting", (key,))
            return Func(name, tuple(self.term(a) for a in e.args))
        if isinstance(e, ast.JsonAccess):
            return Func(f"json{e.op}", (self.term(e.base), self.term(e.key)))
        if isinstance(e, ast.Cast):
            return self.term(e.operand)  # identity is preserved across a cast
        if isinstance(e, ast.Binary):
            return Func(f"op{e.op}", (self.term(e.left), self.term(e.right)))
        if isinstance(e, ast.Unary):
            return Func(f"un{e.op}", (self.term(e.operand),))
        if isinstance(e, ast.Unparsed):
            return Var(f"~{e.text}")
        return Var(f"?{expr_key(e)}")

    def _cname(self, c: ast.Col) -> str:
        qual = c.qualifier or self.table
        return f"{qual}.{c.name}".lower()


def _lit(value: object) -> Term:
    from .smt import Lit

    return Lit(value)


# --------------------------------------------------------------------------- #
# Rendering an expression back to readable SQL (for findings and reports).
# --------------------------------------------------------------------------- #
_OP_DISPLAY = {"and": "AND", "or": "OR"}


def render_expr(e: ast.Expr) -> str:
    if isinstance(e, ast.Col):
        return f"{e.qualifier}.{e.name}" if e.qualifier else e.name
    if isinstance(e, ast.Literal):
        if e.kind == "null":
            return "NULL"
        if e.kind == "bool":
            return "true" if e.value else "false"
        if e.kind == "str":
            return f"'{e.value}'"
        return str(e.value)
    if isinstance(e, ast.FuncCall):
        return f"{e.name}({', '.join(render_expr(a) for a in e.args)})"
    if isinstance(e, ast.Binary):
        op = _OP_DISPLAY.get(e.op, e.op)
        return f"{render_expr(e.left)} {op} {render_expr(e.right)}"
    if isinstance(e, ast.Unary):
        return f"NOT {render_expr(e.operand)}" if e.op == "not" else f"-{render_expr(e.operand)}"
    if isinstance(e, ast.IsNullExpr):
        return f"{render_expr(e.operand)} IS {'NOT ' if e.negated else ''}NULL"
    if isinstance(e, ast.InList):
        items = ", ".join(render_expr(i) for i in e.items)
        return f"{render_expr(e.operand)} {'NOT ' if e.negated else ''}IN ({items})"
    if isinstance(e, ast.Cast):
        return f"{render_expr(e.operand)}::{e.type_name}"
    if isinstance(e, ast.JsonAccess):
        return f"{render_expr(e.base)} {e.op} {render_expr(e.key)}"
    if isinstance(e, ast.Unparsed):
        return e.text
    return "<expr>"


def expr_key(e: ast.Expr) -> str:
    """A stable canonical string, so identical sub-expressions map to one atom."""
    return render_expr(e)
