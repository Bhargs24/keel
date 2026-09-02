"""`keel init` -- the recommended path must work for a stranger, first try."""

from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import tool

import keel_kit


def test_init_scaffolds_a_full_project(project: Path) -> None:
    assert (project / "tools" / "keel.py").exists()
    assert (project / ".claude" / "settings.json").exists()
    assert (project / ".git").exists()
    files = [p for p in project.rglob("*") if p.is_file() and ".git" not in p.parts]
    assert len(files) > 120


def test_roster_is_generated_for_the_real_user(project: Path) -> None:
    """The template's example roster must never become the live one: a user
    who ran `keel init --name Casey` is Casey, not Alex or Sam."""
    roster = (project / "tracker" / "people.toml").read_text(encoding="utf-8")
    assert "[people.casey]" in roster
    assert "alex" not in roster.lower() and "sam" not in roster.lower()
    assert (project / "tracker" / "people.example.toml").exists()


def test_name_falls_back_to_git_identity(tmp_path: Path) -> None:
    dst = tmp_path / "p2"
    dst.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=dst, check=True)
    subprocess.run(["git", "config", "user.name", "Jordan Lee"], cwd=dst, check=True)
    assert keel_kit.main(["init", str(dst)]) == 0
    roster = (dst / "tracker" / "people.toml").read_text(encoding="utf-8")
    assert "[people.jordanlee]" in roster


def test_runtime_directories_exist(project: Path) -> None:
    """Dirs the hooks and commands write into must exist from day one."""
    for rel in ("docs/20-WORK/crossings", "docs/30-CHANGELOG", "docs/40-HANDOFF"):
        assert (project / rel).is_dir(), rel


def test_reinit_never_clobbers(project: Path) -> None:
    marker = project / "CLAUDE.md"
    marker.write_text("MY EDITS", encoding="utf-8")
    assert keel_kit.main(["init", str(project), "--name", "Other"]) == 0
    assert marker.read_text(encoding="utf-8") == "MY EDITS"
    roster = (project / "tracker" / "people.toml").read_text(encoding="utf-8")
    assert "[people.casey]" in roster  # first owner survives a re-init


def test_first_tracker_command_just_works(project: Path) -> None:
    """The bug this pins: a fresh `keel init` user could not run a single
    tracker command ('cannot tell who you are'). Solo projects must resolve
    identity with zero configuration."""
    r = tool(project, "tools/track.py", "add", "T-001", "--title", "smoke")
    assert r.returncode == 0, r.stderr
    assert (project / "tracker" / "tasks" / "T-001.md").exists()


def test_version_flag(capsys) -> None:
    try:
        keel_kit.main(["--version"])
    except SystemExit as e:
        assert e.code == 0
    assert keel_kit.__version__ in capsys.readouterr().out
