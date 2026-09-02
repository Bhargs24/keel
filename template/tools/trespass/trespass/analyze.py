"""The analysis: for every table, command, and internet-facing role, decide
whether an attacker can reach a row they should not -- and prove it either way.

The shape of every check is the same, and it is the whole idea of the tool:

    can the policy make a row visible/writable that the *intent* does not allow?

If yes, the solver hands back a concrete world and we render it as an exploit
(VULNERABLE). If no, the solver has proved it cannot happen (ISOLATED). If the
policy leans on something we could not model, we say so (UNKNOWN). Nothing is
ever guessed into a hard verdict.
"""

from __future__ import annotations

from . import intent as intent_mod
from .encode import SESSION_ROLE, SESSION_UID, Encoder, render_expr
from .findings import Finding, Report, Severity, Verdict, Witness
from .intent import AUTHENTICATED, NOBODY, PUBLIC, Intent, TableIntent
from .schema import Policy, Schema, Table, build_schema
from .smt import (
    FALSE,
    TRUE,
    And,
    Eq,
    Formula,
    IsNull,
    IsTrue,
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
from .smt.solver import Model, SolverBudgetExceeded, solve
from .smt.terms import walk_terms
from .sql import ast

_READ_COMMANDS = ("select", "update", "delete")
_WRITE_COMMANDS = ("insert", "update")


def analyze(
    sql: str,
    intent: Intent | None = None,
    *,
    assume_default_grants: bool = True,
) -> Report:
    schema = build_schema(sql)
    if intent is None:
        intent = intent_mod.infer_intent(schema)
    report = Report(tables_analyzed=len(schema.tables))
    if intent.source == "declared":
        _check_intent_alignment(report, schema, intent)
    for table in schema.tables.values():
        report.policies_analyzed += len(table.policies)
        _check_table(report, schema, table, intent, assume_default_grants)
    return report


def _check_intent_alignment(report: Report, schema: Schema, intent: Intent) -> None:
    """A declared intent that does not line up with the schema must fail loudly.

    A typo'd table or tenant column would otherwise disable the isolation checks
    it was meant to power -- the worst possible failure mode for a rigor tool is
    a green run that verified nothing.
    """
    for tname, ti in intent.tables.items():
        table = schema.table(tname)
        if table is None:
            report.add(
                Finding(
                    rule="intent-unknown-table",
                    verdict=Verdict.UNKNOWN,
                    severity=Severity.MEDIUM,
                    table=tname,
                    title=f"Intent declares `{tname}`, which is not in the schema",
                    detail=(
                        f"The intent file has a `[{tname}]` section but no such table "
                        "was found in the analyzed SQL. Nothing was verified for it -- "
                        "check for a typo or a missing migration file."
                    ),
                    intent_source=intent.source,
                )
            )
        elif ti.tenant is not None and not table.has_column(ti.tenant):
            report.add(
                Finding(
                    rule="intent-unknown-column",
                    verdict=Verdict.UNKNOWN,
                    severity=Severity.HIGH,
                    table=tname,
                    title=f"Intent names tenant column `{ti.tenant}`, which `{tname}` does not have",
                    detail=(
                        f"The intent for `{tname}` says rows are owned via `{ti.tenant}`, "
                        "but the table has no such column. Every isolation check for this "
                        "table was skipped, not passed -- fix the column name to get real "
                        "verdicts."
                    ),
                    intent_source=intent.source,
                )
            )


# --------------------------------------------------------------------------- #
def _check_table(
    report: Report,
    schema: Schema,
    table: Table,
    intent: Intent,
    assume_default_grants: bool,
) -> None:
    ti = intent.for_table(table.name)

    reachable = {
        cmd: schema.api_access(table.name, cmd, assume_default_grants=assume_default_grants)
        for cmd in ("select", "insert", "update", "delete")
    }
    any_reachable = sorted({r for roles in reachable.values() for r in roles})

    # 1. Row-level security switched off on a table the internet can reach.
    if not table.rls_enabled:
        if any_reachable:
            _emit_rls_disabled(report, table, any_reachable, reachable)
        return  # Postgres ignores policies without RLS; nothing else applies.

    # 2. Policies that reference a column that does not exist -- silently dead.
    _check_unknown_columns(report, table)

    # 3. The core isolation / forgery checks, per command and role.
    isolated_combos = 0
    for command in ("select", "insert", "update", "delete"):
        for role in sorted(reachable[command]):
            isolated_combos += _check_combo(report, table, ti, intent, command, role)

    # A table that survived every check with something actually proved.
    if isolated_combos and not any(
        f.table == table.name and f.verdict is Verdict.VULNERABLE for f in report.findings
    ):
        report.add(
            Finding(
                rule="isolated",
                verdict=Verdict.ISOLATED,
                severity=Severity.INFO,
                table=table.name,
                title="Tenant isolation proved",
                detail=(
                    f"Across {isolated_combos} command/role combinations, no policy "
                    "lets a caller reach a row the intent does not allow. The solver "
                    "found no counterexample -- this is a proof, not a scan result."
                ),
                intent_source=intent.source,
            )
        )


# --------------------------------------------------------------------------- #
def _check_combo(
    report: Report,
    table: Table,
    ti: TableIntent | None,
    intent: Intent,
    command: str,
    role: str,
) -> int:
    """Run the isolation and/or forgery checks for one (command, role) pair.

    Returns the number of combinations that were *proved* isolated, so the caller
    can report a positive result when nothing was found.
    """
    isolated = 0

    # Read side: which existing rows can this caller see / delete / update?
    if command in _READ_COMMANDS:
        actual = _actual_formula(table, command, role, clause="using")
        isolated += _isolation_check(
            report, table, ti, intent, command, role, actual, side="read"
        )

    # Write side: what rows can this caller create or re-attribute?
    if command in _WRITE_COMMANDS:
        actual = _actual_formula(table, command, role, clause="check")
        isolated += _isolation_check(
            report, table, ti, intent, command, role, actual, side="write"
        )

    return isolated


def _isolation_check(
    report: Report,
    table: Table,
    ti: TableIntent | None,
    intent: Intent,
    command: str,
    role: str,
    actual: Formula | None,
    *,
    side: str,
) -> int:
    if actual is None:
        return 0  # no policy grants this -> denied -> trivially isolated

    scenario, nonnull = _scenario(role, table)

    # Anonymous writes are almost always a mistake, intent or no intent.
    if role == "anon" and command in _WRITE_COMMANDS and ti is None:
        try:
            model = solve([actual, *scenario], nonnull=nonnull)
        except SolverBudgetExceeded:
            return 0
        if model is not None:
            report.add(_anon_write_finding(table, command, model, actual, intent))
        return 0

    if ti is None or ti.tenant is None or not table.has_column(ti.tenant):
        return 0  # nothing to say about isolation without a notion of ownership

    level = ti.level(command)
    intended = _intended_formula(level, ti, table)

    try:
        model = solve([actual, *scenario], deny=[intended], nonnull=nonnull)
    except SolverBudgetExceeded:
        report.add(
            Finding(
                rule="budget",
                verdict=Verdict.UNKNOWN,
                severity=Severity.LOW,
                table=table.name,
                command=command,
                role=role,
                title="Policy too large to decide exactly",
                detail="The combined policy exceeded the solver's exact budget; "
                "treat this table as unverified rather than safe.",
                intent_source=intent.source,
            )
        )
        return 0

    if model is None:
        return 1  # proved isolated for this combination

    report.add(
        _hole_finding(table, ti, intent, command, role, actual, model, side, level)
    )
    return 0


# --------------------------------------------------------------------------- #
# Formula construction.
# --------------------------------------------------------------------------- #
def _actual_formula(
    table: Table, command: str, role: str, *, clause: str
) -> Formula | None:
    enc = Encoder(table.name)
    permissive: list[Formula] = []
    restrictive: list[Formula] = []
    for policy in table.policies:
        if not policy.applies_to(command, role):
            continue
        expr = _policy_expr(policy, clause)
        f = TRUE if expr is None else enc.formula(expr)
        (permissive if policy.permissive else restrictive).append(f)
    if not permissive:
        return None
    return and_(or_(*permissive), *restrictive)


def _policy_expr(policy: Policy, clause: str) -> ast.Expr | None:
    if clause == "using":
        return policy.using
    # Write side: WITH CHECK, falling back to USING as Postgres itself does.
    return policy.check if policy.check is not None else policy.using


def _intended_formula(level: str, ti: TableIntent, table: Table) -> Formula:
    if level == PUBLIC:
        return TRUE
    if level == NOBODY:
        return FALSE
    if level == AUTHENTICATED:
        return not_(IsNull(SESSION_UID))
    # OWNER / tenant-scoped: the row's owner must be the caller.
    assert ti.tenant is not None
    owner = Var(f"{table.name}.{ti.tenant}".lower())
    return Eq(owner, ti.identity_term())


def _scenario(role: str, table: Table) -> tuple[list[Formula], frozenset[Term]]:
    nonnull: set[Term] = {SESSION_ROLE}
    for col in table.columns.values():
        if col.not_null:
            nonnull.add(Var(f"{table.name}.{col.name}".lower()))
    if role == "anon":
        return [IsNull(SESSION_UID), Eq(SESSION_ROLE, Lit("anon"))], frozenset(nonnull)
    nonnull.add(SESSION_UID)
    return (
        [not_(IsNull(SESSION_UID)), Eq(SESSION_ROLE, Lit("authenticated"))],
        frozenset(nonnull),
    )


# --------------------------------------------------------------------------- #
# Findings.
# --------------------------------------------------------------------------- #
def _emit_rls_disabled(
    report: Report,
    table: Table,
    any_reachable: list[str],
    reachable: dict[str, set[str]],
) -> None:
    role = "anon" if "anon" in any_reachable else any_reachable[0]
    writable = sorted({c for c in ("insert", "update", "delete") if role in reachable[c]})
    effect = "read every row in the table"
    if writable:
        effect += " -- and " + ", ".join(writable) + " them"
    report.add(
        Finding(
            rule="rls-disabled",
            verdict=Verdict.VULNERABLE,
            severity=Severity.CRITICAL,
            table=table.name,
            command="select",
            role=role,
            title="Row-level security is off on an internet-reachable table",
            detail=(
                "PostgREST exposes this table to the "
                f"`{role}` role and row-level security is not enabled, so every "
                "policy you might write is bypassed. Any visitor can "
                f"{effect}."
            ),
            witness=Witness(
                session={"role": role, "auth.uid()": "null" if role == "anon" else "any"},
                row={"(any row)": ""},
                query=f"select * from {table.name};",
                effect="returns every row, to an unauthenticated caller",
            ),
            fix=(
                f"alter table {table.name} enable row level security;\n"
                "-- then add a policy, e.g.\n"
                f"create policy owner_read on {table.name} for select\n"
                "  to authenticated using (user_id = auth.uid());"
            ),
        )
    )


def _hole_finding(
    table: Table,
    ti: TableIntent,
    intent: Intent,
    command: str,
    role: str,
    actual: Formula,
    model: Model,
    side: str,
    level: str,
) -> Finding:
    labels = _Labeler(model)
    attacker = labels.name(SESSION_UID)
    tenant_term = Var(f"{table.name}.{ti.tenant}".lower())
    victim = labels.name(tenant_term)

    precondition = _precondition(actual, model)
    conditional = precondition is not None
    inferred = intent.source == "inferred"
    # A witness resting on something we could not model -- an opaque predicate,
    # or a value marked unparsed (a subquery in term position, which may well be
    # correlated with the session) -- asserts a world we cannot prove reachable.
    # A concrete column flag (`is_public = true`) is a real row that can exist;
    # the rest honestly degrades the verdict to UNKNOWN.
    hard_opaque = any(not n.startswith("col:") for n in _opaque_names(actual)) or any(
        isinstance(t, Var) and t.name.startswith(("~", "?")) for t in _terms_in(actual)
    )

    if hard_opaque or (inferred and conditional):
        verdict, severity = Verdict.UNKNOWN, Severity.MEDIUM
    else:
        verdict, severity = Verdict.VULNERABLE, (
            Severity.CRITICAL if command in ("select",) else Severity.HIGH
        )

    role_disp = "anonymous" if role == "anon" else role
    if side == "write":
        title = f"A caller can {command} a row they do not own"
        query = _write_query(table, ti, command, victim)
        effect = f"creates/modifies a row attributed to `{victim}`, not the caller"
        rule = "forgery"
    else:
        title = f"{role_disp.capitalize()} caller can {command} another user's rows"
        query = f"select * from {table.name};" if command == "select" else _rowop_query(
            table, ti, command, victim
        )
        effect = f"returns rows owned by `{victim}` to `{attacker}`"
        rule = "tenant-read"

    policy = next(
        (p for p in table.policies if p.applies_to(command, role) and p.permissive), None
    )
    policy_expr = None
    if policy is not None:
        raw = policy.using if side == "read" else (policy.check or policy.using)
        policy_expr = render_expr(raw) if raw is not None else None

    session = {"role": role, "auth.uid()": attacker}
    row = {ti.tenant or "owner": victim}
    if conditional and precondition:
        row.update(precondition.row)

    detail = (
        f"The intent for `{table.name}` says {command.upper()} is {level}"
        + (f" (inferred from the `{ti.tenant}` column)" if inferred else "")
        + ". The policy is more permissive than that: the solver found a caller "
        "who is not the row's owner and can still reach it."
    )
    if conditional and precondition:
        detail += f" This holds for {precondition.text}."
    if hard_opaque:
        detail += (
            " The counterexample depends on a predicate that was not modeled "
            "precisely, so this is reported as UNKNOWN rather than a proven hole."
        )

    return Finding(
        rule=rule,
        verdict=verdict,
        severity=severity,
        table=table.name,
        command=command,
        role=role,
        title=title,
        detail=detail,
        policy=policy.name if policy else None,
        policy_expr=policy_expr,
        witness=Witness(
            session=session,
            row=row,
            query=query,
            effect=effect,
            precondition=precondition.text if precondition else None,
        ),
        fix=_fix_hint(table, ti, command, level, side),
        intent_source=intent.source,
    )


def _anon_write_finding(
    table: Table, command: str, model: Model, actual: Formula, intent: Intent
) -> Finding:
    precondition = _precondition(actual, model)
    return Finding(
        rule="anon-write",
        verdict=Verdict.VULNERABLE if precondition is None else Verdict.UNKNOWN,
        severity=Severity.HIGH,
        table=table.name,
        command=command,
        role="anon",
        title=f"An anonymous caller can {command} rows",
        detail=(
            f"A policy grants the `anon` role permission to {command} on "
            f"`{table.name}`. Unauthenticated writes are almost never intended."
        ),
        witness=Witness(
            session={"role": "anon", "auth.uid()": "null"},
            row={"(attacker-controlled)": ""},
            query=_write_query(table, None, command, "anything"),
            effect="an unauthenticated caller changes stored data",
            precondition=precondition.text if precondition else None,
        ),
        fix=f"Restrict the {command} policy on {table.name} to `to authenticated` "
        "and gate it on ownership.",
        intent_source=intent.source,
    )


def _check_unknown_columns(report: Report, table: Table) -> None:
    for policy in table.policies:
        for expr in (policy.using, policy.check):
            if expr is None:
                continue
            for col in _columns_in(expr):
                if col.qualifier in (None, table.name) and not table.has_column(col.name):
                    report.add(
                        Finding(
                            rule="unknown-column",
                            verdict=Verdict.UNKNOWN,
                            severity=Severity.MEDIUM,
                            table=table.name,
                            policy=policy.name,
                            title=f"Policy references unknown column `{col.name}`",
                            detail=(
                                f"Policy `{policy.name}` compares against `{col.name}`, "
                                f"which is not a column of `{table.name}`. The policy may "
                                "not restrict what its author believed it did."
                            ),
                        )
                    )


# --------------------------------------------------------------------------- #
# Witness rendering helpers.
# --------------------------------------------------------------------------- #
class _Labeler:
    """Give equivalence classes friendly names in an exploit (attacker/victim)."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self._names: dict[Term, str] = {}
        self._pool = ["victim", "other-user", "user-c", "user-d"]

    def name(self, term: Term) -> str:
        if self.model.is_null(term):
            return "null"
        root = self.model.class_of(term)
        if root not in self._names:
            if term is SESSION_UID or root == self.model.class_of(SESSION_UID):
                self._names[root] = "attacker"
            else:
                self._names[root] = self._pool.pop(0) if self._pool else "someone-else"
        return self._names[root]


class _Precondition:
    def __init__(self, text: str, row: dict[str, str]) -> None:
        self.text = text
        self.row = row


def _precondition(actual: Formula, model: Model) -> _Precondition | None:
    """If the exploit needs an opaque predicate to hold (a flag, a function), turn
    it into a readable precondition instead of pretending it is unconditional."""
    conditions: list[str] = []
    row: dict[str, str] = {}
    for name in _opaque_names(actual):
        if model.opaque.get(name) and model.opaque[name].value == "true":
            label = name.split(":", 1)[-1]
            if name.startswith("col:"):
                col = label.split(".")[-1]
                conditions.append(f"`{col}` is true")
                row[col] = "true"
            else:
                conditions.append(f"`{label}` holds")
    if not conditions:
        return None
    return _Precondition("any row where " + " and ".join(conditions), row)


def _opaque_names(f: Formula) -> set[str]:
    out: set[str] = set()
    if isinstance(f, Opaque):
        out.add(f.name)
    elif isinstance(f, Not | IsTrue):
        out |= _opaque_names(f.f)
    elif isinstance(f, And | Or):
        for sub in f.fs:
            out |= _opaque_names(sub)
    return out


def _terms_in(f: Formula) -> set[Term]:
    """Every term (and sub-term) a formula touches."""
    out: set[Term] = set()
    if isinstance(f, Eq):
        out.update(walk_terms(f.a))
        out.update(walk_terms(f.b))
    elif isinstance(f, IsNull):
        out.update(walk_terms(f.t))
    elif isinstance(f, Not | IsTrue):
        out |= _terms_in(f.f)
    elif isinstance(f, And | Or):
        for sub in f.fs:
            out |= _terms_in(sub)
    return out


def _columns_in(e: ast.Expr) -> list[ast.Col]:
    if isinstance(e, ast.Col):
        return [e]
    out: list[ast.Col] = []
    for field_name in getattr(e, "__dataclass_fields__", {}):
        val = getattr(e, field_name)
        if isinstance(val, ast.Expr):
            out.extend(_columns_in(val))
        elif isinstance(val, tuple):
            for item in val:
                if isinstance(item, ast.Expr):
                    out.extend(_columns_in(item))
    return out


def _write_query(table: Table, ti: TableIntent | None, command: str, victim: str) -> str:
    col = ti.tenant if ti and ti.tenant else "user_id"
    if command == "insert":
        return f"insert into {table.name} ({col}, ...) values ('{victim}', ...);"
    return f"update {table.name} set {col} = '{victim}' where id = '...';"


def _rowop_query(table: Table, ti: TableIntent, command: str, victim: str) -> str:
    col = ti.tenant or "user_id"
    if command == "delete":
        return f"delete from {table.name} where {col} = '{victim}';"
    return f"update {table.name} set ... where {col} = '{victim}';"


def _fix_hint(table: Table, ti: TableIntent, command: str, level: str, side: str) -> str:
    col = ti.tenant or "user_id"
    ident = "auth.uid()" if ti.identity_kind == "uid" else f"auth.jwt() ->> '{ti.identity_claim}'"
    if side == "write":
        return (
            f"Add a WITH CHECK so a caller can only write their own rows:\n"
            f"  create policy {command}_own on {table.name} for {command}\n"
            f"    to authenticated with check ({col} = {ident});"
        )
    return (
        f"Tighten the policy to owner-only, matching the intent ({level}):\n"
        f"  using ({col} = {ident})"
    )
