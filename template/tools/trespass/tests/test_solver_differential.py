"""Differential test: our from-scratch solver vs. Z3, on random formulas.

The custom solver is the product; Z3 is the oracle. We generate thousands of
random three-valued formulas over a fixed vocabulary and assert that our solver
and a faithful Z3 encoding agree on satisfiability every single time. When they
disagree, the failure message prints the exact formula so it can be turned into
a permanent regression case.

Z3 has no native Kleene logic, so we encode each formula's value as a pair of
booleans ``(is_true, is_false)`` -- both false means NULL -- which is the
standard way to lift three-valued logic into a two-valued solver.

Skipped automatically if ``z3-solver`` is not installed, so the runtime stays
dependency-free.
"""

from __future__ import annotations

import random

import pytest

from trespass.smt import (
    NULL,
    And,
    BoolF,
    Eq,
    Formula,
    Func,
    IsNull,
    IsTrue,
    Lit,
    Not,
    Opaque,
    Or,
    Term,
    Var,
)
from trespass.smt.solver import solve

z3 = pytest.importorskip("z3")


# A small fixed vocabulary keeps formulas dense enough to hit edge cases.
_VARS = [Var("a"), Var("b"), Var("c")]
_LITS = [Lit("p"), Lit("q")]
_TERMS: list[Term] = [*_VARS, *_LITS, NULL]
_OPAQUES = ["o1", "o2"]


def _rand_term(rng: random.Random, depth: int) -> Term:
    if depth > 0 and rng.random() < 0.25:
        return Func("f", (_rand_term(rng, depth - 1),))
    return rng.choice(_TERMS)


def _rand_formula(rng: random.Random, depth: int) -> Formula:
    if depth <= 0:
        kind = rng.choice(["eq", "isnull", "opaque", "bool"])
    else:
        kind = rng.choice(
            ["eq", "isnull", "opaque", "not", "and", "or", "istrue", "eq", "eq"]
        )
    if kind == "eq":
        return Eq(_rand_term(rng, 1), _rand_term(rng, 1))
    if kind == "isnull":
        return IsNull(_rand_term(rng, 1))
    if kind == "opaque":
        return Opaque(rng.choice(_OPAQUES), nullable=rng.random() < 0.5)
    if kind == "bool":
        return BoolF(rng.random() < 0.5)
    if kind == "not":
        return Not(_rand_formula(rng, depth - 1))
    if kind == "istrue":
        return IsTrue(_rand_formula(rng, depth - 1))
    n = rng.randint(2, 3)
    fs = tuple(_rand_formula(rng, depth - 1) for _ in range(n))
    return And(fs) if kind == "and" else Or(fs)


class _Z3Encoder:
    """Faithful Kleene encoding into Z3: each node -> (is_true, is_false)."""

    def __init__(self) -> None:
        self.s = z3.Solver()
        self._term_val: dict[Term, object] = {}
        self._term_null: dict[Term, object] = {}
        self._opaque: dict[str, tuple[object, object]] = {}
        self._lit_id: dict[object, int] = {}

    def term(self, t: Term) -> tuple[object, object]:
        """Return (value:Int, is_null:Bool) for a term, creating it once."""
        if t in self._term_val:
            return self._term_val[t], self._term_null[t]
        if isinstance(t, Lit) and t.value is None:
            val = z3.IntVal(-1)
            null = z3.BoolVal(True)
        elif isinstance(t, Lit):
            val = z3.IntVal(self._lit_code(t.value))
            null = z3.BoolVal(False)
        elif isinstance(t, Func):
            val = z3.Int(f"fv_{id(t)}")
            null = z3.Bool(f"fn_{id(t)}")
            self._add_congruence(t, val, null)
        else:  # Var
            val = z3.Int(f"v_{t.name}")
            null = z3.Bool(f"n_{t.name}")
        self._term_val[t] = val
        self._term_null[t] = null
        return val, null

    def _lit_code(self, value: object) -> int:
        if value not in self._lit_id:
            self._lit_id[value] = 100 + len(self._lit_id)
        return self._lit_id[value]

    def _add_congruence(self, t: Func, val: object, null: object) -> None:
        # equal, non-null args of same-named funcs => equal, matching-null results
        for other, oval in list(self._term_val.items()):
            if isinstance(other, Func) and other.name == t.name and len(other.args) == len(t.args):
                onull = self._term_null[other]
                arg_pairs = [(self.term(a), self.term(b)) for a, b in zip(other.args, t.args, strict=True)]
                same_args = z3.And([
                    z3.And(z3.Not(an), z3.Not(bn), av == bv)
                    for (av, an), (bv, bn) in arg_pairs
                ]) if arg_pairs else z3.BoolVal(True)
                self.s.add(z3.Implies(same_args, z3.And(val == oval, null == onull)))

    def eval(self, f: Formula) -> tuple[object, object]:
        """Return (is_true, is_false) Bools for a formula."""
        if isinstance(f, BoolF):
            return z3.BoolVal(f.value), z3.BoolVal(not f.value)
        if isinstance(f, Eq):
            av, an = self.term(f.a)
            bv, bn = self.term(f.b)
            both = z3.And(z3.Not(an), z3.Not(bn))
            return z3.And(both, av == bv), z3.And(both, av != bv)
        if isinstance(f, IsNull):
            _, n = self.term(f.t)
            return n, z3.Not(n)
        if isinstance(f, Opaque):
            if f.name not in self._opaque:
                it = z3.Bool(f"ot_{f.name}")
                iff = z3.Bool(f"of_{f.name}")
                if f.nullable:
                    self.s.add(z3.Not(z3.And(it, iff)))
                else:
                    self.s.add(it != iff)
                self._opaque[f.name] = (it, iff)
            return self._opaque[f.name]
        if isinstance(f, Not):
            it, iff = self.eval(f.f)
            return iff, it
        if isinstance(f, IsTrue):
            it, _ = self.eval(f.f)
            return it, z3.Not(it)  # two-valued: false whenever not true
        if isinstance(f, And):
            parts = [self.eval(x) for x in f.fs]
            is_true = z3.And([t for t, _ in parts])
            is_false = z3.Or([fa for _, fa in parts])
            return is_true, is_false
        if isinstance(f, Or):
            parts = [self.eval(x) for x in f.fs]
            is_true = z3.Or([t for t, _ in parts])
            is_false = z3.And([fa for _, fa in parts])
            return is_true, is_false
        raise TypeError(f)

    def sat_when_true(self, f: Formula) -> bool:
        it, _ = self.eval(f)
        self.s.add(it)
        return self.s.check() == z3.sat


@pytest.mark.parametrize("seed", range(400))
def test_matches_z3(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(8):  # several formulas per seed -> a few thousand total
        f = _rand_formula(rng, depth=rng.randint(1, 3))
        ours = solve([f]) is not None
        theirs = _Z3Encoder().sat_when_true(f)
        assert ours == theirs, f"disagree on {f!r}: ours={ours} z3={theirs}"
