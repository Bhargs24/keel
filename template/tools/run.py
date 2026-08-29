#!/usr/bin/env python3
"""The cross-platform task runner. Works on Windows, macOS, and Linux with only
Python - no `make`, no bash, nothing to install.

    python tools/run.py check      the fast gate (placeholders, boundaries,
                                    ownership, tracker, tenant isolation)
    python tools/run.py secure     prove tenant isolation on the schema (trespass)
    python tools/run.py board      the progress board in a browser
    python tools/run.py hooks      install the git hooks
    python tools/run.py phase      which pipeline phase, and the next command
    python tools/run.py verify     everything: the fast gate + your lint/types/tests

`make` still works on macOS/Linux and calls straight into this file, so there is
exactly one source of truth for what a gate does. On Windows, use this directly.

Why this exists: the gates are the part Keel is supposed to hide from you, so
they must never be the thing that breaks in your face because a build tool from
1976 is not installed. Everything here is the Python standard library.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PY = sys.executable


def _run(args: list[str], cwd: Path = ROOT) -> int:
    """Run a subprocess, streaming its output, and return its exit code."""
    return subprocess.run(args, cwd=cwd).returncode


def _schema_path() -> str | None:
    for cand in ("supabase/migrations", "schema.sql", "db/schema.sql",
                 "sql/schema.sql", "prisma/schema.prisma"):
        if (ROOT / cand).exists():
            return cand
    return None


# --------------------------------------------------------------------------- #
# Tasks.
# --------------------------------------------------------------------------- #
def task_check() -> int:
    """The fast gate. Seconds, no toolchains. Run before every push."""
    steps = [
        ("no placeholder code", [PY, str(TOOLS / "no_placeholders.py")]),
        ("module boundaries", [PY, str(TOOLS / "dep_check.py")]),
        ("ownership boundary", [PY, str(TOOLS / "ownership_check.py")]),
        ("tracker consistent", [PY, str(TOOLS / "track.py"), "check"]),
    ]
    failed = []
    for name, args in steps:
        if _run(args) != 0:
            failed.append(name)
    if task_secure(quiet_if_absent=True) != 0:
        failed.append("tenant isolation (trespass)")
    if failed:
        print(f"\n>> gate FAILED: {', '.join(failed)}")
        return 1
    print("\n>> fast gate passed. `python tools/run.py verify` also runs lint, types, tests.")
    return 0


def task_secure(quiet_if_absent: bool = False) -> int:
    """Prove tenant isolation on the database schema with trespass."""
    schema = _schema_path()
    if not schema:
        if not quiet_if_absent:
            print(">> trespass: no schema yet (looked for supabase/migrations, "
                  "schema.sql, ...). Nothing to prove.")
        return 0
    print(f">> trespass: proving tenant isolation on {schema}")
    return _run([PY, str(TOOLS / "trespass" / "run.py"), "check", schema, "--no-color"])


def task_board() -> int:
    """The progress board in a browser."""
    return _run([PY, str(TOOLS / "board.py")])


def task_phase() -> int:
    return _run([PY, str(TOOLS / "track.py"), "phase"])


def task_docs() -> int:
    return _run([PY, str(TOOLS / "track.py"), "docs"])


def task_hooks() -> int:
    """Install the git hooks (refuses a push to the default branch)."""
    rc = _run(["git", "config", "core.hooksPath", ".githooks"])
    if rc == 0:
        print(">> hooks installed. Override a push to the default branch "
              "deliberately with ALLOW_PUSH_DEFAULT=1.")
    return rc


def task_verify() -> int:
    """Everything: the fast gate, then your language lint/typecheck/tests."""
    if task_check() != 0:
        return 1
    # The language jobs live in the Makefile (they are stack-specific). Use them
    # if `make` is available; otherwise the fast gate is what you get until the
    # architect wires the stack's commands into this runner.
    if _has_make():
        return _run(["make", "lint", "typecheck", "test"])
    print("\n>> lint/typecheck/test are stack-specific. Once /architect picks the "
          "stack, wire their commands into task_verify() here (or use `make` on "
          "macOS/Linux). The fast gate above is cross-platform and always runs.")
    return 0


def _has_make() -> bool:
    from shutil import which
    return which("make") is not None


TASKS = {
    "check": task_check,
    "secure": task_secure,
    "board": task_board,
    "phase": task_phase,
    "docs": task_docs,
    "hooks": task_hooks,
    "verify": task_verify,
}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        print("tasks: " + ", ".join(TASKS))
        return 0 if argv else 2
    task = argv[0]
    if task not in TASKS:
        print(f"run.py: unknown task {task!r}. Known: {', '.join(TASKS)}", file=sys.stderr)
        return 2
    return TASKS[task]() or 0


if __name__ == "__main__":
    raise SystemExit(main())
