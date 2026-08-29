"""A small, from-scratch decision procedure for the RLS fragment.

This is a satisfiability solver for quantifier-free formulas over the theory of
equality with uninterpreted functions (QF_UF / EUF), extended with an explicit
``NULL`` value and three-valued Kleene evaluation. That is exactly -- and only --
the fragment that row-level-security policies live in, which is what keeps it
tractable and correct.

Why write one instead of importing Z3? Three reasons, in order of importance:

1. **Zero runtime dependencies.** ``git clone && python -m trespass`` works
   forever, on any machine, with no wheels to resolve. For a tool people are
   meant to trust and run against their own database, that matters.
2. **The formulas are tiny.** A policy has a handful of atoms. A general SMT
   solver is enormous machinery for a problem that a careful enumeration decides
   exactly.
3. **It is checkable.** Because the fragment is small, the solver can be
   *differentially tested against Z3* (see ``tests/test_solver_differential.py``)
   on thousands of random formulas. The custom code is the product; Z3 is the
   oracle that proves the custom code right.

The method is deliberately simple and obviously-correct rather than clever:

* Enumerate the finitely-many *shapes* a model can take -- which terms are null,
  which equalities hold, which opaque atoms are true.
* For each shape, close equality under congruence with a union-find and reject
  it if it contradicts a decided disequality or merges two distinct literals.
* Evaluate the asserted formulas in Kleene logic. If they all come out ``TRUE``,
  that shape is a model, and we hand it back as a witness.

Small-model reasoning makes this complete: the only facts a formula can observe
are its own atoms, so ranging over their consistent truth-assignments ranges
over every model that matters.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

from .terms import (
    And,
    BoolF,
    Eq,
    Formula,
    Func,
    IsNull,
    K,
    Not,
    Opaque,
    Or,
    Term,
    Var,
    is_nonnull_literal,
    is_null_literal,
    k_and,
    k_not,
    k_or,
    walk_terms,
)


class SolverBudgetExceeded(Exception):
    """Raised when a formula has too many atoms to enumerate exactly.

    Callers treat this as *unknown*, never as *safe* -- the honest response to a
    formula we did not fully decide.
    """


# Guard against pathological inputs. RLS policies sit far below this; a formula
# that blows the budget is reported as UNKNOWN rather than silently mis-decided.
_MAX_COMBOS = 1_000_000


@dataclass
class Model:
    """A satisfying assignment -- a concrete world in which the asserted formulas
    are all ``TRUE``. This is the witness rendered into an exploit later on.
    """

    #: Terms that are NULL in this model.
    null_terms: frozenset[Term]
    #: Map from each non-null term to its equivalence-class representative.
    _root: dict[Term, Term]
    #: Truth value chosen for each opaque atom.
    opaque: dict[str, K]

    def is_null(self, t: Term) -> bool:
        return t in self.null_terms

    def same_class(self, a: Term, b: Term) -> bool:
        """Whether two non-null terms denote the same value in this model."""
        return self._root.get(a, a) == self._root.get(b, b)

    def class_of(self, t: Term) -> Term:
        return self._root.get(t, t)


class _UnionFind:
    __slots__ = ("parent",)

    def __init__(self) -> None:
        self.parent: dict[Term, Term] = {}

    def find(self, t: Term) -> Term:
        p = self.parent.get(t, t)
        if p is t or p == t:
            self.parent[t] = t
            return t
        root = self.find(p)
        self.parent[t] = root
        return root

    def union(self, a: Term, b: Term) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            # Prefer literals as representatives so classes carry a concrete value.
            if is_nonnull_literal(rb):
                ra, rb = rb, ra
            self.parent[rb] = ra


# --------------------------------------------------------------------------- #
# Atom collection.
# --------------------------------------------------------------------------- #
@dataclass
class _Atoms:
    terms: list[Term]
    eqs: list[Eq]
    opaques: dict[str, bool]  # name -> nullable


def _collect(formulas: list[Formula]) -> _Atoms:
    terms: dict[Term, None] = {}
    eqs: dict[Eq, None] = {}
    opaques: dict[str, bool] = {}

    def visit_term(t: Term) -> None:
        for sub in walk_terms(t):
            terms.setdefault(sub, None)

    def visit(f: Formula) -> None:
        if isinstance(f, BoolF):
            return
        if isinstance(f, Eq):
            visit_term(f.a)
            visit_term(f.b)
            eqs.setdefault(f, None)
        elif isinstance(f, IsNull):
            visit_term(f.t)
        elif isinstance(f, Opaque):
            opaques[f.name] = opaques.get(f.name, False) or f.nullable
        elif isinstance(f, Not):
            visit(f.f)
        elif isinstance(f, And | Or):
            for sub in f.fs:
                visit(sub)

    for f in formulas:
        visit(f)
    return _Atoms(list(terms), list(eqs), opaques)


# --------------------------------------------------------------------------- #
# Evaluation of a formula inside a candidate model.
# --------------------------------------------------------------------------- #
def _eval(
    f: Formula,
    null_terms: set[Term],
    uf: _UnionFind,
    opaque_vals: dict[str, K],
) -> K:
    if isinstance(f, BoolF):
        return K.TRUE if f.value else K.FALSE
    if isinstance(f, Eq):
        if f.a in null_terms or f.b in null_terms:
            return K.NULL
        return K.TRUE if uf.find(f.a) == uf.find(f.b) else K.FALSE
    if isinstance(f, IsNull):
        return K.TRUE if f.t in null_terms else K.FALSE
    if isinstance(f, Opaque):
        return opaque_vals[f.name]
    if isinstance(f, Not):
        return k_not(_eval(f.f, null_terms, uf, opaque_vals))
    if isinstance(f, And):
        return k_and([_eval(x, null_terms, uf, opaque_vals) for x in f.fs])
    if isinstance(f, Or):
        return k_or([_eval(x, null_terms, uf, opaque_vals) for x in f.fs])
    raise TypeError(f"unknown formula node: {f!r}")


# --------------------------------------------------------------------------- #
# The solver proper.
# --------------------------------------------------------------------------- #
def solve(
    assertions: list[Formula],
    *,
    nonnull: frozenset[Term] = frozenset(),
    deny: list[Formula] | None = None,
) -> Model | None:
    """Find a model in which every formula in ``assertions`` evaluates to ``TRUE``
    and every formula in ``deny`` evaluates to something *other* than ``TRUE``.

    Returns a :class:`Model` witness if one exists (SAT), or ``None`` if no such
    world exists (UNSAT -- a proof).

    ``deny`` is what makes intent checking precise. Postgres shows a row only when
    a policy is ``TRUE``; "the intent does *not* grant this" therefore means the
    intent predicate is *not TRUE* -- which is ``FALSE`` **or** ``NULL``, not just
    ``FALSE``. A row an anonymous caller reads under an owner-only intent is the
    canonical case: ``owner = auth.uid()`` is ``NULL`` (not false) when
    ``auth.uid()`` is null, and it must still count as "not permitted".

    ``nonnull`` names terms known never to be null (a role literal, a ``NOT NULL``
    column); it sharpens the analysis without ever making it unsound.

    Raises :class:`SolverBudgetExceeded` if the formula is too large to decide
    exactly -- callers must treat that as *unknown*, not *safe*.
    """
    deny = deny or []
    atoms = _collect(assertions + deny)

    # Which terms may be null in some model?
    nullable_terms = [
        t
        for t in atoms.terms
        if isinstance(t, Var | Func) and t not in nonnull
    ]
    # A NULL literal is always null; every other literal is never null.
    forced_null = {t for t in atoms.terms if is_null_literal(t)}

    eqs = atoms.eqs
    opaque_names = list(atoms.opaques)

    # Enumeration budget: 2^nulls x 2^eqs x (2 or 3)^opaques.
    combos = (
        (2 ** len(nullable_terms))
        * (2 ** len(eqs))
        * _prod(3 if atoms.opaques[n] else 2 for n in opaque_names)
    )
    if combos > _MAX_COMBOS:
        raise SolverBudgetExceeded(f"{combos} candidate models exceeds budget")

    # Distinct non-null literals are provably unequal; record the constraint once.
    literal_terms = [t for t in atoms.terms if is_nonnull_literal(t)]

    opaque_domains = [
        (K.TRUE, K.FALSE, K.NULL) if atoms.opaques[n] else (K.TRUE, K.FALSE)
        for n in opaque_names
    ]

    for null_bits in itertools.product((False, True), repeat=len(nullable_terms)):
        null_terms: set[Term] = set(forced_null)
        for t, bit in zip(nullable_terms, null_bits, strict=True):
            if bit:
                null_terms.add(t)

        for eq_bits in itertools.product((False, True), repeat=len(eqs)):
            uf = _UnionFind()
            # Seed every non-null term as its own singleton class.
            for seed in atoms.terms:
                if seed not in null_terms:
                    uf.find(seed)

            ok = True
            disequal: list[tuple[Term, Term]] = []
            for eq, decide_equal in zip(eqs, eq_bits, strict=True):
                if eq.a in null_terms or eq.b in null_terms:
                    continue  # the atom is NULL; its equal/unequal bit is irrelevant
                if decide_equal:
                    uf.union(eq.a, eq.b)
                else:
                    disequal.append((eq.a, eq.b))

            if not _congruence_close(uf, atoms.terms, null_terms):
                continue

            # Reject models that merge two distinct literal values.
            for i in range(len(literal_terms)):
                for j in range(i + 1, len(literal_terms)):
                    li, lj = literal_terms[i], literal_terms[j]
                    if li in null_terms or lj in null_terms:
                        continue
                    if uf.find(li) == uf.find(lj):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue

            # Reject models that violate a decided disequality.
            if any(uf.find(a) == uf.find(b) for a, b in disequal):
                continue

            for opaque_choice in itertools.product(*opaque_domains) if opaque_names else [()]:
                opaque_vals = dict(zip(opaque_names, opaque_choice, strict=True))
                if all(
                    _eval(f, null_terms, uf, opaque_vals) is K.TRUE for f in assertions
                ) and all(
                    _eval(d, null_terms, uf, opaque_vals) is not K.TRUE for d in deny
                ):
                    roots = {
                        t: uf.find(t) for t in atoms.terms if t not in null_terms
                    }
                    return Model(
                        null_terms=frozenset(null_terms),
                        _root=roots,
                        opaque=opaque_vals,
                    )
    return None


def _congruence_close(
    uf: _UnionFind, terms: list[Term], null_terms: set[Term]
) -> bool:
    """Close equality under congruence, to a fixpoint.

    ``f(x)`` and ``f(y)`` denote the same thing whenever ``x`` and ``y`` do -- and
    "the same thing" means both their *value* and their *null-ness* agree. Two
    consequences, both of which this enforces:

    * If the arguments match, the two applications must be unified (value
      congruence). Without it the solver would think two equal terms could
      differ, and might hand back a spurious exploit -- a false positive.
    * If the arguments match but one application was guessed null and the other
      non-null, the candidate model is impossible: return ``False`` so the caller
      discards it. (This is the case the Z3 differential test caught.)
    """
    funcs = [t for t in terms if isinstance(t, Func)]
    changed = True
    while changed:
        changed = False
        for i in range(len(funcs)):
            for j in range(i + 1, len(funcs)):
                fi, fj = funcs[i], funcs[j]
                if fi.name != fj.name or len(fi.args) != len(fj.args):
                    continue
                # Congruence only fires on provably-equal, non-null arguments.
                args_match = all(
                    a not in null_terms
                    and b not in null_terms
                    and uf.find(a) == uf.find(b)
                    for a, b in zip(fi.args, fj.args, strict=True)
                )
                if not args_match:
                    continue
                fi_null, fj_null = fi in null_terms, fj in null_terms
                if fi_null != fj_null:
                    return False  # equal inputs, contradictory null-ness
                if fi_null and fj_null:
                    continue
                if uf.find(fi) != uf.find(fj):
                    uf.union(fi, fj)
                    changed = True
    return True


def _prod(xs: object) -> int:
    total = 1
    for x in xs:  # type: ignore[attr-defined]
        total *= x
    return total


def is_sat(assertions: list[Formula], *, nonnull: frozenset[Term] = frozenset()) -> bool:
    return solve(assertions, nonnull=nonnull) is not None
