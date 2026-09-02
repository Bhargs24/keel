"""The tracker: lifecycle, the consistency gate, phase detection, and the
identity/timezone behavior the whole build loop rests on."""

from __future__ import annotations

import re
from pathlib import Path

from conftest import tool


def _add(project: Path, tid: str, **kw) -> None:
    args = ["tools/track.py", "add", tid, "--title", kw.get("title", tid)]
    if kw.get("depends"):
        args += ["--depends", kw["depends"]]
    r = tool(project, *args)
    assert r.returncode == 0, r.stderr


def _set_status(project: Path, tid: str, status: str) -> None:
    f = project / "tracker" / "tasks" / f"{tid}.md"
    text = f.read_text(encoding="utf-8")
    f.write_text(re.sub(r"^status: .*$", f"status: {status}", text,
                        count=1, flags=re.MULTILINE), encoding="utf-8")


def test_lifecycle_add_start_log(project: Path) -> None:
    _add(project, "T-001")
    assert tool(project, "tools/track.py", "start", "T-001").returncode == 0
    body = (project / "tracker" / "tasks" / "T-001.md").read_text(encoding="utf-8")
    assert "status: doing" in body and "started:" in body
    assert tool(project, "tools/track.py", "log", "T-001", "did a thing").returncode == 0
    assert "did a thing" in (project / "tracker" / "tasks" / "T-001.md").read_text(
        encoding="utf-8")


def test_check_passes_on_clean_todo_tasks(project: Path) -> None:
    _add(project, "T-001")
    _add(project, "T-002", depends="T-001")
    assert tool(project, "tools/track.py", "check").returncode == 0


def test_check_fails_on_done_with_open_dependency(project: Path) -> None:
    _add(project, "T-001")
    _add(project, "T-002", depends="T-001")
    _set_status(project, "T-002", "done")
    r = tool(project, "tools/track.py", "check")
    assert r.returncode == 1


def test_check_fails_on_unknown_dependency(project: Path) -> None:
    _add(project, "T-002", depends="T-999")
    assert tool(project, "tools/track.py", "check").returncode == 1


def test_track_tz_pins_the_offset(project: Path) -> None:
    r = tool(project, "tools/track.py", "add", "T-TZ", "--title", "tz",
             env={"TRACK_TZ": "+00:00"})
    assert r.returncode == 0, r.stderr
    r = tool(project, "tools/track.py", "start", "T-TZ", env={"TRACK_TZ": "+00:00"})
    assert r.returncode == 0, r.stderr
    body = (project / "tracker" / "tasks" / "T-TZ.md").read_text(encoding="utf-8")
    assert re.search(r"started: .*\+0000", body), body


def test_project_name_comes_from_now_md(project: Path) -> None:
    now = project / "docs" / "10-STATUS" / "NOW.md"
    now.parent.mkdir(parents=True, exist_ok=True)
    now.write_text("Project: Skylark\n\n## Claims\n", encoding="utf-8")
    _add(project, "T-001")
    r = tool(project, "tools/track.py", "status")
    assert "Skylark" in r.stdout


def test_phase_walks_the_pipeline(project: Path) -> None:
    """Phase is a fact about files on disk -- walk the whole journey and check
    each transition, including the /scaffold step that arms the gates."""
    def phase() -> str:
        return tool(project, "tools/track.py", "phase").stdout

    assert "/keel" in phase()
    (project / "spec" / "01-Company").mkdir(parents=True, exist_ok=True)
    (project / "spec" / "01-Company" / "CONCEPT.md").write_text("x", encoding="utf-8")
    assert "/define" in phase()
    (project / "spec" / "02-Product").mkdir(parents=True, exist_ok=True)
    (project / "spec" / "02-Product" / "PRD.md").write_text("x", encoding="utf-8")
    assert "/design" in phase()
    (project / "spec" / "06-Design").mkdir(parents=True, exist_ok=True)
    (project / "spec" / "06-Design" / "DESIGN-BRIEF.md").write_text("x", encoding="utf-8")
    assert "/architect" in phase()
    (project / "spec" / "03-Technical").mkdir(parents=True, exist_ok=True)
    (project / "spec" / "03-Technical" / "BUILD-ROADMAP.md").write_text("x", encoding="utf-8")
    assert "/feasibility" in phase()
    (project / "docs" / "50-AUDITS").mkdir(parents=True, exist_ok=True)
    (project / "docs" / "50-AUDITS" / "2026-01-01-feasibility.md").write_text(
        "GO", encoding="utf-8")
    assert "/plan" in phase()
    _add(project, "T-001")
    # Tasks exist but the repo isn't wired: the guided path must surface
    # /scaffold, or the gates stay unarmed forever.
    assert "/scaffold" in phase()
    (project / "tools" / "boundaries.json").write_text(
        '{"module": "", "layers": {"apps": []}}', encoding="utf-8")
    assert "/next" in phase()
