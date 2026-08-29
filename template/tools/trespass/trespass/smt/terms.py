"""The term and formula algebra the solver reasons over.

Row-level-security policies, once you strip away syntax, are boolean
combinations of a very small set of atoms: equalities between values, null
checks, and opaque predicates we cannot see inside (a subquery, a ``<``
comparison, a call to some ``is_admin()`` function). That fragment is
*decidable*, and small, which is the entire reason this tool can give proofs
instead of guesses.

Two things in here are deliberate and load-bearing:

* **Terms are structural.** Two ``Func("jwt_claim", (Lit("org"),))`` values are
  the same object for reasoning purposes, so ``auth.jwt() ->> 'org'`` written in
  two policies refers to one symbolic value. Frozen dataclasses give us that for
  free via value equality and hashing.

* **Formulas are three-valued.** Postgres evaluates a policy in *Kleene* logic:
  a row is visible only when the ``USING`` expression is ``TRUE`` -- not when it
  is ``FALSE`` and not when it is ``NULL``. Modelling that faithfully is what
  lets us catch the whole family of "``auth.uid()`` is null for an anonymous
  visitor, so the ``=`` yields NULL, so the row is hidden... except when it
  isn't" bugs. See :mod:`trespass.smt.solver` for how ``TRUE`` is asserted.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
# Terms: the things that have values.
# --------------------------------------------------------------------------- #
class Term:
    """Base class for a value-carrying term. Subclasses are frozen and hashable."""


@dataclass(frozen=True)
class Var(Term):
    """A symbolic value: a column of the row under test, or a session value such
    as ``auth.uid()``. Two ``Var``\\ s with the same name denote the same value."""

    name: str


@dataclass(frozen=True)
class Lit(Term):
    """A concrete literal. ``Lit(None)`` is SQL ``NULL`` and is always null;
    every other literal is never null, and two different literal values are
    provably distinct."""

    value: object


@dataclass(frozen=True)
class Func(Term):
    """An uninterpreted application, e.g. ``lower(x)`` or a JSON claim access.

    We do not know what the function computes, but we do know it is a *function*:
    equal arguments give equal results (congruence). The solver enforces that.
    """

    name: str
    args: tuple[Term, ...] = ()


#: SQL ``NULL`` as a term. Always null; never equal to anything, including itself.
NULL: Lit = Lit(None)


def is_null_literal(t: Term) -> bool:
    return isinstance(t, Lit) and t.value is None


def is_nonnull_literal(t: Term) -> bool:
    return isinstance(t, Lit) and t.value is not None


# --------------------------------------------------------------------------- #
# Kleene three-valued logic.
# --------------------------------------------------------------------------- #
class K(enum.Enum):
    """A Kleene truth value."""

    TRUE = "true"
    FALSE = "false"
    NULL = "null"


def k_not(x: K) -> K:
    if x is K.TRUE:
        return K.FALSE
    if x is K.FALSE:
        return K.TRUE
    return K.NULL


def k_and(values: list[K]) -> K:
    # FALSE dominates; then NULL; else TRUE.
    if any(v is K.FALSE for v in values):
        return K.FALSE
    if any(v is K.NULL for v in values):
        return K.NULL
    return K.TRUE


def k_or(values: list[K]) -> K:
    # TRUE dominates; then NULL; else FALSE.
    if any(v is K.TRUE for v in values):
        return K.TRUE
    if any(v is K.NULL for v in values):
        return K.NULL
    return K.FALSE


# --------------------------------------------------------------------------- #
# Formulas: three-valued expressions over terms.
# --------------------------------------------------------------------------- #
class Formula:
    """Base class for a three-valued formula."""


@dataclass(frozen=True)
class BoolF(Formula):
    """A literal ``TRUE`` or ``FALSE`` (never null)."""

    value: bool


@dataclass(frozen=True)
class Eq(Formula):
    """Three-valued equality. NULL if either side is null, else the usual test."""

    a: Term
    b: Term


@dataclass(frozen=True)
class IsNull(Formula):
    """``t IS NULL`` -- two-valued: exactly TRUE or FALSE, never null itself."""

    t: Term


@dataclass(frozen=True)
class Opaque(Formula):
    """A predicate we cannot model precisely: a subquery, an inequality, an
    arbitrary boolean function. ``nullable`` decides whether it may also be NULL.

    Opaque atoms are the honest edge of the analysis. A finding that depends on
    one is reported as UNKNOWN rather than VULNERABLE, so the tool never claims a
    proof it does not have. See :mod:`trespass.analyze`.
    """

    name: str
    nullable: bool = False


@dataclass(frozen=True)
class Not(Formula):
    f: Formula


@dataclass(frozen=True)
class And(Formula):
    fs: tuple[Formula, ...]


@dataclass(frozen=True)
class Or(Formula):
    fs: tuple[Formula, ...]


# Convenience constructors ------------------------------------------------- #
TRUE: BoolF = BoolF(True)
FALSE: BoolF = BoolF(False)


def and_(*fs: Formula) -> Formula:
    flat: list[Formula] = []
    for f in fs:
        if isinstance(f, And):
            flat.extend(f.fs)
        else:
            flat.append(f)
    if not flat:
        return TRUE
    if len(flat) == 1:
        return flat[0]
    return And(tuple(flat))


def or_(*fs: Formula) -> Formula:
    flat: list[Formula] = []
    for f in fs:
        if isinstance(f, Or):
            flat.extend(f.fs)
        else:
            flat.append(f)
    if not flat:
        return FALSE
    if len(flat) == 1:
        return flat[0]
    return Or(tuple(flat))


def not_(f: Formula) -> Formula:
    if isinstance(f, Not):
        return f.f
    return Not(f)


# --------------------------------------------------------------------------- #
# Small helpers used by the encoder and the solver.
# --------------------------------------------------------------------------- #
def walk_terms(t: Term) -> list[Term]:
    """A term and all of its sub-terms (function arguments), depth-first."""
    out = [t]
    if isinstance(t, Func):
        for a in t.args:
            out.extend(walk_terms(a))
    return out


@dataclass
class OpaqueSpec:
    """Bookkeeping for an opaque atom discovered while scanning a formula."""

    name: str
    nullable: bool = field(default=False)
