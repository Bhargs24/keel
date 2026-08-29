"""End-to-end: every shipped example must behave exactly as its folder claims.

``examples/vulnerable/*`` must each produce at least one VULNERABLE finding;
``examples/safe/*`` must produce none. These double as living documentation --
if a change breaks the promise the README makes, a test goes red.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from trespass.analyze import analyze
from trespass.findings import Verdict
from trespass.intent import load_intent

ROOT = Path(__file__).resolve().parent.parent
VULN = sorted((ROOT / "examples" / "vulnerable").glob("*.sql"))
SAFE = sorted((ROOT / "examples" / "safe").glob("*.sql"))

# Examples whose verdict depends on a declared intent file.
_INTENT_FOR = {
    "03-public-or-bypass.sql": "documents.intent",
    "03-public-read-owner-write.sql": "blog.intent",
}


def _intent_for(path: Path):  # type: ignore[no-untyped-def]
    name = _INTENT_FOR.get(path.name)
    if name:
        return load_intent(ROOT / "examples" / "intent" / name)
    return None


def test_examples_exist() -> None:
    assert VULN, "no vulnerable examples found"
    assert SAFE, "no safe examples found"


@pytest.mark.parametrize("path", VULN, ids=[p.name for p in VULN])
def test_vulnerable_examples_are_flagged(path: Path) -> None:
    report = analyze(path.read_text(encoding="utf-8"), _intent_for(path))
    assert report.vulnerabilities, f"{path.name} should have a proven vulnerability"
    # Every vulnerability must carry a reproducible witness.
    for f in report.vulnerabilities:
        assert f.witness is not None and f.witness.query
        assert f.fix


@pytest.mark.parametrize("path", SAFE, ids=[p.name for p in SAFE])
def test_safe_examples_are_clean(path: Path) -> None:
    report = analyze(path.read_text(encoding="utf-8"), _intent_for(path))
    assert report.ok, (
        f"{path.name} should be clean but flagged: "
        + ", ".join(f"{f.rule}:{f.title}" for f in report.vulnerabilities)
    )
    # A safe example should also *prove* something, not merely fail to find a bug.
    assert any(f.verdict is Verdict.ISOLATED for f in report.findings)


def test_missing_rls_reports_unconditional_exploit() -> None:
    path = ROOT / "examples" / "vulnerable" / "01-missing-rls.sql"
    report = analyze(path.read_text(encoding="utf-8"))
    hole = report.vulnerabilities[0]
    assert hole.rule == "rls-disabled"
    assert hole.witness is not None
    assert hole.witness.precondition is None  # nothing conditional about it


def test_intent_turns_ambiguity_into_a_verdict() -> None:
    """The headline feature: the same schema is UNKNOWN under inference and
    VULNERABLE once an owner-only intent is declared."""
    sql = (ROOT / "examples" / "vulnerable" / "03-public-or-bypass.sql").read_text("utf-8")

    inferred = analyze(sql)  # no intent file -> inferred, conservative
    assert not inferred.vulnerabilities
    assert any(f.verdict is Verdict.UNKNOWN for f in inferred.findings)

    declared = analyze(sql, load_intent(ROOT / "examples" / "intent" / "documents.intent"))
    assert declared.vulnerabilities
