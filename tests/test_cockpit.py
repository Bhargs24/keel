"""The cockpit: state detection, the document reader's traversal guard, and
the markdown renderer -- the surfaces a non-technical user actually touches."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load(project: Path):
    """Import the project's own cockpit module, fresh, against that project."""
    for name in ("track", "keel_cockpit_under_test"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(project / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "keel_cockpit_under_test", project / "tools" / "keel.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.pop(0)
        sys.modules.pop("track", None)


def test_state_has_a_step_for_every_phase(project: Path) -> None:
    cockpit = _load(project)
    detected = {"Pre-Discover", "Discovering", "Discover done", "Define done",
                "Design done", "Architect done", "Feasibility done",
                "Plan done", "Building"}
    assert detected == set(cockpit.STEPS), (
        "every phase the detector can return needs a plain-English step card")
    for phase, step in cockpit.STEPS.items():
        assert step["title"] and step["command"] and step["why"], phase


def test_state_serves_the_journey(project: Path) -> None:
    cockpit = _load(project)
    s = cockpit.state()
    assert s["journey"][0] == "Idea" and s["journey"][-1] == "Ship"
    assert s["step"]["command"].startswith("/")
    assert len(s["commands"]) == 3  # pipeline, build loop, anytime


def test_command_count_matches_the_shipped_commands(project: Path) -> None:
    cockpit = _load(project)
    listed = {cmd.split(" ")[0] for _, rows in cockpit.COMMANDS for cmd, _ in rows}
    shipped = {f"/{p.stem}" for p in (project / ".claude" / "commands").glob("*.md")}
    assert listed == shipped, "the cockpit must show exactly the commands that exist"


def test_doc_reader_blocks_traversal(project: Path) -> None:
    cockpit = _load(project)
    (project / "docs" / "note.md").write_text("# hello", encoding="utf-8")
    ok = cockpit.read_doc("docs/note.md")
    assert "error" not in ok
    for bad in ("../secrets.md", "docs/../../outside.md", "/etc/passwd",
                "docs/note.txt", "tracker/people.toml"):
        assert "error" in cockpit.read_doc(bad), bad


def test_markdown_renderer_escapes_html(project: Path) -> None:
    cockpit = _load(project)
    html = cockpit.md_to_html("# Title\n\n<script>alert(1)</script>\n\n`code`")
    assert "<h1" in html and "<code>code</code>" in html
    assert "<script>" not in html
