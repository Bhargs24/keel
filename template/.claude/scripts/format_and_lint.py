"""PostToolUse: quietly format what just changed, with whatever the repo uses.

Stack-agnostic on purpose: a formatter runs only when BOTH its config exists
in this repo AND the tool is installed. Nothing here ever fails the hook --
formatting is a courtesy, not a gate -- and nothing assumes a directory
layout. Stdlib only, cross-platform.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which

ROOT = Path(__file__).resolve().parents[2]


def _changed_suffixes() -> set[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {Path(p).suffix for p in out.splitlines() if p.strip()}


def _quiet(args: list[str]) -> None:
    try:
        subprocess.run(args, cwd=ROOT, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        pass


def main() -> int:
    changed = _changed_suffixes()
    if not changed:
        return 0
    if ".py" in changed and which("ruff"):
        # tools/trespass is vendored upstream code: keep it byte-identical to
        # its pin, never restyle it.
        _quiet(["ruff", "format", "--exclude", "tools/trespass", "."])
        _quiet(["ruff", "check", "--fix", "--exclude", "tools/trespass", "."])
    if changed & {".ts", ".tsx", ".js", ".jsx"}:
        if (ROOT / "biome.json").exists() and which("npx"):
            _quiet(["npx", "--no-install", "biome", "check", "--write", "."])
        elif (ROOT / ".prettierrc").exists() and which("npx"):
            _quiet(["npx", "--no-install", "prettier", "--write", "."])
    if ".go" in changed and (ROOT / "go.mod").exists() and which("gofmt"):
        _quiet(["gofmt", "-w", "."])
    if ".dart" in changed and (ROOT / "pubspec.yaml").exists() and which("dart"):
        _quiet(["dart", "format", "."])
    if ".rs" in changed and (ROOT / "Cargo.toml").exists() and which("cargo"):
        _quiet(["cargo", "fmt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
