"""Hand-verified unit tests for the core decision procedure.

These pin the semantics the rest of the tool relies on: three-valued equality,
distinct literals, congruence, and -- most importantly -- the two canonical
row-level-security shapes (owner-only is provably safe; owner-or-public is
provably broken).
"""

from __future__ import annotations

import pytest

from trespass.smt import NULL, And, Eq, Func, IsNull, Lit, Opaque, Var, not_, or_, solve
from trespass.smt.solver import SolverBudgetExceeded, is_sat


def test_trivial_equality_is_sat() -> None:
    x, y = Var("x"), Var("y")
    assert is_sat([Eq(x, y)])  # x and y can simply be equal


def test_equality_and_its_negation_is_unsat() -> None:
    x, y = Var("x"), Var("y")
    # asserting Eq TRUE and Not(Eq) TRUE means Eq is both true and false.
    assert not is_sat([Eq(x, y), not_(Eq(x, y))])


def test_distinct_literals_never_equal() -> None:
    assert not is_sat([Eq(Lit("a"), Lit("b"))])
    assert is_sat([Eq(Lit("a"), Lit("a"))])


def test_transitivity_is_enforced() -> None:
    a, b, c = Var("a"), Var("b"), Var("c")
    # a=b, b=c, but a<>c is impossible.
    assert not is_sat([Eq(a, b), Eq(b, c), not_(Eq(a, c))])


def test_null_equality_is_not_true() -> None:
    # x = NULL can never evaluate TRUE, whatever x is.
    x = Var("x")
    assert not is_sat([Eq(x, NULL)])
    # ...but IS NULL can be satisfied.
    assert is_sat([IsNull(x)])


def test_congruence_of_functions() -> None:
    a, b = Var("a"), Var("b")
    fa, fb = Func("f", (a,)), Func("f", (b,))
    # a=b forces f(a)=f(b); asserting f(a)<>f(b) alongside is impossible.
    assert not is_sat([Eq(a, b), not_(Eq(fa, fb))])
    # without a=b, f(a) and f(b) may differ.
    assert is_sat([not_(Eq(fa, fb))])


def test_nonnull_hint_sharpens_but_stays_sound() -> None:
    x = Var("x")
    # With no hint, x IS NULL is satisfiable.
    assert is_sat([IsNull(x)])
    # Declaring x non-null makes the same assertion unsatisfiable.
    assert not is_sat([IsNull(x)], nonnull=frozenset({x}))


# --------------------------------------------------------------------------- #
# The two shapes the whole tool exists to tell apart.
# --------------------------------------------------------------------------- #
def _select_hole(policy_using, *, owner, session):  # type: ignore[no-untyped-def]
    """A SELECT hole exists iff the policy makes a row visible to a session that
    is *not* the row's owner (and the session is a real, logged-in user)."""
    return [
        policy_using,  # the row is visible...
        not_(Eq(owner, session)),  # ...to someone who is not its owner...
        not_(IsNull(session)),  # ...who is actually authenticated.
    ]


def test_owner_only_policy_is_isolated() -> None:
    # USING (user_id = auth.uid())
    row_owner = Var("orders.user_id")
    uid = Var("auth.uid")
    policy = Eq(row_owner, uid)
    assert solve(_select_hole(policy, owner=row_owner, session=uid)) is None


def test_owner_or_public_policy_is_vulnerable() -> None:
    # USING (user_id = auth.uid() OR is_public)
    row_owner = Var("orders.user_id")
    uid = Var("auth.uid")
    policy = or_(Eq(row_owner, uid), Opaque("orders.is_public", nullable=True))
    model = solve(_select_hole(policy, owner=row_owner, session=uid))
    assert model is not None
    # The witness must exploit the public flag, not ownership.
    from trespass.smt import K

    assert model.opaque["orders.is_public"] is K.TRUE
    assert not model.same_class(row_owner, uid)


def test_using_true_is_vulnerable() -> None:
    from trespass.smt import TRUE

    row_owner = Var("orders.user_id")
    uid = Var("auth.uid")
    assert solve(_select_hole(TRUE, owner=row_owner, session=uid)) is not None


def test_org_scoped_multitenant_is_isolated() -> None:
    # USING (org_id = (auth.jwt() ->> 'org_id')) -- textbook multi-tenant policy.
    row_org = Var("docs.org_id")
    jwt_org = Func("jwt_claim", (Lit("org_id"),))
    policy = Eq(row_org, jwt_org)
    hole = [policy, not_(Eq(row_org, jwt_org)), not_(IsNull(jwt_org))]
    assert solve(hole) is None


def test_budget_is_exceeded_loudly() -> None:
    # A wide conjunction of independent equalities blows the enumeration budget;
    # the solver must raise rather than silently return "safe".
    big = And(tuple(Eq(Var(f"a{i}"), Var(f"b{i}")) for i in range(30)))
    with pytest.raises(SolverBudgetExceeded):
        solve([big])
