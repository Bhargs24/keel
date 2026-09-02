"""The vendored trespass copy: pinned, licensed, and actually correct.

A stale vendored security tool is worse than none -- it once shipped a version
that printed 'proved isolated' over a leaking schema. These tests make that
class of drift impossible to ship silently.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDORED = REPO / "template" / "tools" / "trespass"


def _run_trespass(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VENDORED / "run.py"), *args],
                          capture_output=True, text=True, timeout=120)


def test_pin_matches_the_code() -> None:
    pin = re.search(r"\| Version \| ([\d.]+) \|",
                    (VENDORED / "VENDORED.md").read_text(encoding="utf-8"))
    version = re.search(r'__version__ = "([\d.]+)"',
                        (VENDORED / "trespass" / "__init__.py").read_text(encoding="utf-8"))
    assert pin and version
    assert pin.group(1) == version.group(1), (
        "VENDORED.md and the vendored code disagree -- re-run "
        "scripts/vendor_trespass.py instead of editing either by hand")


def test_license_ships_with_the_copy() -> None:
    assert (VENDORED / "LICENSE").exists()
    assert "MIT" in (VENDORED / "LICENSE").read_text(encoding="utf-8")


def test_vulnerable_example_is_flagged() -> None:
    r = _run_trespass("check", str(VENDORED / "examples" / "vulnerable" / "02-using-true.sql"),
                      "--no-color")
    assert r.returncode == 1
    assert "VULNERABLE" in r.stdout


def test_safe_example_is_proved() -> None:
    r = _run_trespass("check", str(VENDORED / "examples" / "safe" / "01-owner-only.sql"),
                      "--no-color")
    assert r.returncode == 0


def test_the_false_proof_regression_stays_dead() -> None:
    """v0.1.0 'proved isolation' on this leaky policy (two IS TRUE tests
    collapsed into one atom). The vendored copy must flag it, forever."""
    schema = (
        "create table posts (id uuid primary key, user_id uuid not null,\n"
        "  is_public boolean, deleted boolean);\n"
        "alter table posts enable row level security;\n"
        "create policy read on posts for select to authenticated\n"
        "  using (user_id = auth.uid() or (is_public is true and not (deleted is true)));\n"
    )
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        sql = Path(td) / "schema.sql"
        sql.write_text(schema, encoding="utf-8")
        intent = Path(td) / "app.intent"
        intent.write_text("[posts]\ntenant = user_id\nselect = owner\n", encoding="utf-8")
        r = _run_trespass("check", str(sql), "--intent", str(intent), "--no-color")
    assert r.returncode == 1
    assert "VULNERABLE" in r.stdout
    assert "proved isolated" not in r.stdout.lower()
