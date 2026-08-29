"""What the analyzer produces: findings, verdicts, and reproducible witnesses.

A finding is never just an opinion. When the verdict is ``VULNERABLE`` it carries
a :class:`Witness` -- concrete session and row values, plus the SQL that
demonstrates the hole -- because a security tool that cannot show you the exploit
is asking you to take its word for it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Verdict(enum.Enum):
    """The four things the analyzer can conclude about a check.

    ``UNKNOWN`` is a first-class result, not a failure: it is the tool refusing to
    claim a proof it does not have (a policy leans on a subquery we did not model,
    say). Reporting "I could not decide this" is what keeps the other verdicts
    trustworthy.
    """

    VULNERABLE = "vulnerable"
    ISOLATED = "isolated"
    UNKNOWN = "unknown"
    INFO = "info"


class Severity(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def rank(self) -> int:
        return {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}[self.value]


@dataclass
class Witness:
    """A concrete, reproducible demonstration of a hole."""

    #: Session facts, e.g. {"auth.uid()": "attacker", "role": "authenticated"}.
    session: dict[str, str]
    #: The offending row's relevant column values, e.g. {"user_id": "victim"}.
    row: dict[str, str]
    #: A SQL statement an attacker could run to reproduce the effect.
    query: str
    #: One line describing what that statement does.
    effect: str
    #: If the exploit needs a precondition (a row where some flag holds), state it.
    precondition: str | None = None


@dataclass
class Finding:
    rule: str
    verdict: Verdict
    severity: Severity
    table: str
    title: str
    detail: str
    command: str | None = None
    role: str | None = None
    policy: str | None = None
    policy_expr: str | None = None
    witness: Witness | None = None
    fix: str | None = None
    intent_source: str = "none"  # "declared" | "inferred" | "none"

    def sort_key(self) -> tuple[int, int, str, str]:
        # Vulnerable first, then by severity, then stable by table/rule.
        verdict_rank = {"vulnerable": 3, "unknown": 2, "info": 1, "isolated": 0}
        return (
            -verdict_rank[self.verdict.value],
            -self.severity.rank,
            self.table,
            self.rule,
        )


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    tables_analyzed: int = 0
    policies_analyzed: int = 0

    def add(self, f: Finding) -> None:
        self.findings.append(f)

    def sorted(self) -> list[Finding]:
        return sorted(self.findings, key=lambda f: f.sort_key())

    def counts(self) -> dict[str, int]:
        c = {v.value: 0 for v in Verdict}
        for f in self.findings:
            c[f.verdict.value] += 1
        return c

    @property
    def vulnerabilities(self) -> list[Finding]:
        return [f for f in self.findings if f.verdict is Verdict.VULNERABLE]

    @property
    def ok(self) -> bool:
        """True when nothing is provably vulnerable."""
        return not self.vulnerabilities
