"""The quality gates: each one must fire when it should, stay quiet when it
should, and the runner must never call an unarmed gate 'passed'."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import git, tool


# ------------------------------------------------------------- no_placeholders
def test_placeholder_in_source_fails(project: Path) -> None:
    (project / "src").mkdir()
    (project / "src" / "x.ts").write_text("// TODO: fix later\n", encoding="utf-8")
    assert tool(project, "tools/no_placeholders.py").returncode == 1


def test_placeholder_with_work_item_is_allowed(project: Path) -> None:
    (project / "src").mkdir()
    (project / "src" / "x.ts").write_text(
        "// TODO: harden retry  WORK-ITEM: T-042\n", encoding="utf-8")
    assert tool(project, "tools/no_placeholders.py").returncode == 0


# ------------------------------------------------------------------ dep_check
def test_dep_check_inactive_without_config(project: Path) -> None:
    r = tool(project, "tools/dep_check.py")
    assert r.returncode == 0
    assert "no module boundaries configured" in r.stdout


def test_dep_check_enforces_layers(project: Path) -> None:
    (project / "tools" / "boundaries.json").write_text(json.dumps({
        "module": "",
        "layers": {"apps": ["packages"], "packages": ["packages"]},
        "siblings_isolated": ["apps"],
        "leaf": ["packages/shared"],
    }), encoding="utf-8")
    (project / "packages" / "shared").mkdir(parents=True)
    (project / "packages" / "shared" / "core.py").write_text(
        "from packages.util import x\n", encoding="utf-8")
    (project / "packages" / "util").mkdir(parents=True)
    (project / "packages" / "util" / "u.py").write_text("x = 1\n", encoding="utf-8")
    r = tool(project, "tools/dep_check.py")
    assert r.returncode == 1
    assert "must import nothing internal" in r.stdout


def test_dep_check_clean_layout_passes(project: Path) -> None:
    (project / "tools" / "boundaries.json").write_text(json.dumps({
        "module": "",
        "layers": {"apps": ["packages"], "packages": ["packages"]},
    }), encoding="utf-8")
    (project / "apps" / "web").mkdir(parents=True)
    (project / "apps" / "web" / "a.py").write_text(
        "from packages.core import x\n", encoding="utf-8")
    (project / "packages" / "core").mkdir(parents=True)
    (project / "packages" / "core" / "c.py").write_text("x = 1\n", encoding="utf-8")
    assert tool(project, "tools/dep_check.py").returncode == 0


# ------------------------------------------------------------ ownership_check
def _two_person_setup(project: Path) -> str:
    (project / "tracker" / "people.toml").write_text(
        '[people.casey]\ndisplay = "Casey"\nrole = "founder"\n\n'
        '[people.sam]\ndisplay = "Sam"\nrole = "developer"\n', encoding="utf-8")
    (project / "docs" / "20-WORK" / "OWNERSHIP.map").write_text(
        "web/   SAM\ngen/   GENERATED\ntools/ CASEY\n", encoding="utf-8")
    (project / "web").mkdir()
    (project / "web" / "app.txt").write_text("v1\n", encoding="utf-8")
    (project / "gen").mkdir()
    (project / "gen" / "out.txt").write_text("v1\n", encoding="utf-8")
    git(project, "config", "user.email", "t@example.test")
    git(project, "config", "user.name", "Casey")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    return git(project, "rev-parse", "HEAD").stdout.strip()


def test_ownership_quiet_on_default_branch(project: Path) -> None:
    _two_person_setup(project)
    r = tool(project, "tools/ownership_check.py")
    assert r.returncode == 0
    assert "nothing to check" in r.stdout


def test_ownership_blocks_cross_owner_edit(project: Path) -> None:
    base = _two_person_setup(project)
    git(project, "switch", "-q", "-c", "casey/T-1-thing")
    (project / "web" / "app.txt").write_text("edited by casey\n", encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "cross edit")
    r = tool(project, "tools/ownership_check.py", base)
    assert r.returncode == 1
    assert "belong to" in r.stdout


def test_ownership_blocks_hand_edited_generated(project: Path) -> None:
    base = _two_person_setup(project)
    git(project, "switch", "-q", "-c", "casey/T-2-thing")
    (project / "gen" / "out.txt").write_text("hand edit\n", encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "hand edit")
    r = tool(project, "tools/ownership_check.py", base)
    assert r.returncode == 1
    assert "GENERATED" in r.stdout


def test_ownership_allows_own_area(project: Path) -> None:
    base = _two_person_setup(project)
    git(project, "switch", "-q", "-c", "casey/T-3-thing")
    (project / "tools" / "note.txt").write_text("mine\n", encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "own edit")
    assert tool(project, "tools/ownership_check.py", base).returncode == 0


# ------------------------------------------------------------------ the runner
def test_gate_summary_is_honest_when_unarmed(project: Path) -> None:
    """A fresh project has almost nothing to enforce. The runner must say so
    -- 'inactive' by name -- and never print a blanket 'passed'."""
    r = tool(project, "tools/run.py", "check")
    assert r.returncode == 0
    assert "inactive" in r.stdout
    assert "armed by /scaffold" in r.stdout


def test_gate_fails_loudly_on_a_real_violation(project: Path) -> None:
    (project / "src").mkdir()
    (project / "src" / "x.py").write_text("# TODO: finish\n", encoding="utf-8")
    r = tool(project, "tools/run.py", "check")
    assert r.returncode == 1
    assert "FAILED" in r.stdout
