"""CLI behavior: exit codes (for CI) and output formats."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trespass.cli import main

ROOT = Path(__file__).resolve().parent.parent


def _vuln(tmp_path: Path) -> Path:
    p = tmp_path / "schema.sql"
    p.write_text(
        "create table orders (id uuid, user_id uuid not null);\n"
        "grant select on orders to anon;",
        encoding="utf-8",
    )
    return p


def _safe(tmp_path: Path) -> Path:
    p = tmp_path / "schema.sql"
    p.write_text(
        "create table s (id uuid, user_id uuid not null);\n"
        "alter table s enable row level security;\n"
        "create policy r on s for select to authenticated using (user_id = auth.uid());",
        encoding="utf-8",
    )
    return p


def test_exit_nonzero_on_vulnerability(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["check", str(_vuln(tmp_path)), "--no-color"])
    assert code == 1
    assert "VULNERABLE" in capsys.readouterr().out


def test_exit_zero_when_clean(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["check", str(_safe(tmp_path)), "--no-color"])
    assert code == 0


def test_fail_on_unknown(tmp_path: Path) -> None:
    # A schema whose only issue is UNKNOWN should pass by default but fail with --fail-on unknown.
    p = tmp_path / "s.sql"
    p.write_text(
        "create table docs (id uuid, user_id uuid not null, is_public boolean);\n"
        "alter table docs enable row level security;\n"
        "create policy r on docs for select to authenticated "
        "using (user_id = auth.uid() or is_public);",
        encoding="utf-8",
    )
    assert main(["check", str(p), "--no-color"]) == 0
    assert main(["check", str(p), "--no-color", "--fail-on", "unknown"]) == 1


def test_json_output_is_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(["check", str(_vuln(tmp_path)), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["counts"]["vulnerable"] >= 1


def test_sarif_output_is_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(["check", str(_vuln(tmp_path)), "--sarif"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["results"][0]["level"] == "error"


def test_stdin_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    import io

    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO("create table t (id uuid, user_id uuid not null);\ngrant select on t to anon;"),
    )
    assert main(["check", "-", "--no-color"]) == 1


def test_missing_path_is_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "does-not-exist.sql"]) == 2


def test_directory_is_scanned(tmp_path: Path) -> None:
    (tmp_path / "a.sql").write_text("create table t (id uuid);", encoding="utf-8")
    (tmp_path / "b.sql").write_text("grant select on t to anon;", encoding="utf-8")
    # Combined, the two files describe an exposed table with no RLS.
    assert main(["check", str(tmp_path), "--no-color"]) == 1
