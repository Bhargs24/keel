"""SessionStart: load the state so nobody has to know a command exists.

Claude reads this and acts on it; the developer never has to ask. Stdlib
only, cross-platform.
"""

from __future__ import annotations

import contextlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Never crash on a legacy Windows code page: force UTF-8, replace what can't render.
for _stream in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=15
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _track(*args: str) -> list[str]:
    try:
        out = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "track.py"), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
        return out.splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return []


def main() -> int:
    print("════════ SESSION BRIEF ════════\n")
    print("You are the operator. Run the tools yourself. Never ask the developer to")
    print(
        "run a command you can run. Never ask them to open the board or the tracker.\n"
    )

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    print("── branch ──")
    print(f"  {branch or '(no repository yet)'}")
    if branch in ("main", "master"):
        print("  ON MAIN. Work goes on a branch: <person>/<TASK-ID>-<slug>.")
        print("  Create it yourself before the first edit. Never push to main.")
    elif branch and "/" not in branch:
        print("  This branch declares no owner, so the ownership check will refuse it.")
        print("  Rename it to <person>/<TASK-ID>-<slug> yourself.")

    now_md = ROOT / "docs" / "10-STATUS" / "NOW.md"
    if now_md.exists():
        lines = now_md.read_text(encoding="utf-8").splitlines()
        claims, inside = [], False
        for line in lines:
            if line.startswith("## Claims"):
                inside = True
                continue
            if inside and line.startswith("## "):
                break
            if inside and line.startswith("|"):
                claims.append(line)
        if claims:
            print("\n── claimed right now (docs/10-STATUS/NOW.md) ──")
            for c in claims[:8]:
                print(f"  {c}")

    phase = _track("phase")
    if phase:
        print("\n── pipeline phase ──")
        for line in phase[1:4]:
            print(f"  {line}")

    tasks_dir = ROOT / "tracker" / "tasks"
    if tasks_dir.exists() and any(tasks_dir.glob("*.md")):
        print("\n── tracker ──")
        for line in _track("status")[:6]:
            print(f"  {line}")
        print("\n── ready to start ──")
        for line in _track("next")[2:9]:
            print(f"  {line}")
        print("\n── waiting on the other person ──")
        for line in _track("blocked")[1:10]:
            print(f"  {line}")
        print(
            "\n  Board: python tools/board.py   (open it for them, do not tell them to)"
        )

    spec = ROOT / "spec"
    if spec.exists() and not any(
        p for p in spec.rglob("*.md") if p.name != "README.md"
    ):
        print("\n  spec/ IS EMPTY. The pipeline has not started -- begin with /keel.")

    print("\nFirst move: read docs/00-RULES/THE-RULEBOOK.md. It is the one book.")
    print("═════════════════════════════════════")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
