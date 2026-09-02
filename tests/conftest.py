"""Fixtures: every test runs against a real scaffolded project in tmp_path,
driving the shipped tools the way a user (or an AI session) would -- through
`keel init` and subprocesses -- so the tests exercise the actual product
surface, not a mock of it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import keel_kit  # noqa: E402


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A freshly scaffolded Keel project owned by 'Casey'."""
    dst = tmp_path / "proj"
    rc = keel_kit.main(["init", str(dst), "--name", "Casey"])
    assert rc == 0
    return dst


def tool(project: Path, *args: str, env: dict | None = None,
         stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run a shipped tool inside the project, exactly as a user would."""
    import os
    merged = dict(os.environ)
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, *args], cwd=project, capture_output=True,
        timeout=120, env=merged, input=stdin,
        # The tools emit UTF-8 (box-drawing and all); decode it as such no
        # matter what code page this console happens to use.
        encoding="utf-8", errors="replace",
    )


def git(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=project, capture_output=True,
                          text=True, timeout=60)


@pytest.fixture
def committed_project(project: Path) -> Path:
    """The scaffolded project with an identity configured and everything
    committed -- the state after a real first session's setup."""
    git(project, "config", "user.email", "casey@example.test")
    git(project, "config", "user.name", "Casey")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "scaffold")
    return project
