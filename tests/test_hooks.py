"""The Claude Code hooks: cross-platform Python, correct blocking semantics,
and no noise when there is nothing to say."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import tool


def _scan(project: Path, content: str):
    payload = json.dumps({"tool_input": {"content": content}})
    return tool(project, ".claude/scripts/secret_scan.py", stdin=payload)


def test_secret_scan_blocks_with_exit_2(project: Path) -> None:
    """Exit 2 is the code that actually blocks a tool call; exit 1 only warns.
    This pins the blocking semantics the docs promise."""
    r = _scan(project, 'api_key = "sk-live-abcdef1234567890abc"')
    assert r.returncode == 2
    assert "BLOCKED" in r.stderr


def test_secret_scan_allows_placeholders(project: Path) -> None:
    assert _scan(project, 'api_key = "YOUR_KEY_HERE_EXAMPLE"').returncode == 0
    assert _scan(project, 'password = "xxxxxxxxxxxxxxxx"').returncode == 0
    assert _scan(project, "const total = price * qty").returncode == 0


def test_secret_scan_survives_garbage_input(project: Path) -> None:
    assert tool(project, ".claude/scripts/secret_scan.py",
                stdin="not json at all").returncode == 0


def test_hooks_survive_legacy_windows_codepage(project: Path) -> None:
    """The box-drawing output must never crash on cp1252 -- the exact failure
    a Windows user hits when hook output is piped."""
    for script in ("session_brief.py", "handoff_reminder.py", "preamble.py"):
        r = tool(project, f".claude/scripts/{script}",
                 env={"PYTHONIOENCODING": "cp1252"})
        assert r.returncode == 0, f"{script}: {r.stderr}"


def test_handoff_reminder_quiet_before_the_build(committed_project: Path) -> None:
    """No tasks, nothing uncommitted: the Stop hook must say nothing at all.
    A warning that always fires trains everyone to ignore it."""
    r = tool(committed_project, ".claude/scripts/handoff_reminder.py")
    assert r.returncode == 0
    assert "BEFORE YOU STOP" not in r.stdout


def test_handoff_reminder_flags_uncommitted_work(committed_project: Path) -> None:
    (committed_project / "stray.txt").write_text("wip", encoding="utf-8")
    r = tool(committed_project, ".claude/scripts/handoff_reminder.py")
    assert "UNCOMMITTED CHANGES" in r.stdout


def test_settings_json_uses_python_everywhere(project: Path) -> None:
    """The hooks must not depend on bash/cat existing -- that is the Windows
    promise, kept mechanically."""
    settings = json.loads((project / ".claude" / "settings.json").read_text(
        encoding="utf-8"))
    commands = [h["command"]
                for hooks in settings["hooks"].values()
                for entry in hooks
                for h in entry["hooks"]]
    assert commands, "no hooks registered?"
    for cmd in commands:
        assert cmd.startswith("python "), cmd
