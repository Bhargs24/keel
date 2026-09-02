"""A tiny SMT solver for the row-level-security fragment, plus the term and
formula algebra it works over.

Public surface:

* Terms -- :class:`~trespass.smt.terms.Var`, :class:`~trespass.smt.terms.Lit`,
  :class:`~trespass.smt.terms.Func`, and :data:`~trespass.smt.terms.NULL`.
* Formulas -- :class:`~trespass.smt.terms.Eq`, :class:`~trespass.smt.terms.IsNull`,
  :class:`~trespass.smt.terms.Opaque`, and the connectives ``and_ / or_ / not_``.
* Solving -- :func:`~trespass.smt.solver.solve` returns a witness
  :class:`~trespass.smt.solver.Model` or ``None``.
"""

from __future__ import annotations

from .solver import Model, SolverBudgetExceeded, is_sat, solve
from .terms import (
    FALSE,
    NULL,
    TRUE,
    And,
    BoolF,
    Eq,
    Formula,
    Func,
    IsNull,
    IsTrue,
    K,
    Lit,
    Not,
    Opaque,
    Or,
    Term,
    Var,
    and_,
    not_,
    or_,
)

__all__ = [
    "FALSE",
    "NULL",
    "TRUE",
    "And",
    "BoolF",
    "Eq",
    "Formula",
    "Func",
    "IsNull",
    "IsTrue",
    "K",
    "Lit",
    "Model",
    "Not",
    "Opaque",
    "Or",
    "SolverBudgetExceeded",
    "Term",
    "Var",
    "and_",
    "is_sat",
    "not_",
    "or_",
    "solve",
]
