"""Stop hook: check the wrap-up ceremony actually happened, rather than hoping.

Warns when in-flight tasks have no log entry today, when changes sit
uncommitted, or when a build in progress has no handoff written today.
Stdlib only, cross-platform, never blocks (exit 0 always).
"""

from __future__ import annotations

import contextlib
import datetime as dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Never crash on a legacy Windows code page: force UTF-8, replace what can't render.
for _stream in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    warn: list[str] = []
    today = dt.date.today().isoformat()

    tasks_dir = ROOT / "tracker" / "tasks"
    task_files = sorted(tasks_dir.glob("*.md")) if tasks_dir.exists() else []
    stale = []
    for f in task_files:
        text = f.read_text(encoding="utf-8")
        if "status: doing" in text and f"- {today}" not in text:
            stale.append(f.stem)
    if stale:
        warn.append(
            f"  IN FLIGHT WITH NO ENTRY TODAY: {' '.join(stale)}\n"
            '    Run: python tools/track.py log <ID> "what happened"\n'
            "    Do it now, yourself. Do not ask the developer to."
        )

    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        dirty = ""
    if dirty:
        warn.append(
            "  UNCOMMITTED CHANGES. Commit them, or say plainly what is left and why."
        )

    # A build in progress deserves a handoff. Quiet before the build starts.
    handoff_dir = ROOT / "docs" / "40-HANDOFF"
    if task_files:
        handoffs = sorted(handoff_dir.glob("*.md")) if handoff_dir.exists() else []
        if not any(h.name.startswith(today) for h in handoffs):
            warn.append(
                f"  NO HANDOFF TODAY. Write docs/40-HANDOFF/{today}-<slug>.md:\n"
                "    what is done, what is half-done, the next action, and what you know\n"
                "    that is not written anywhere. Write it yourself."
            )

    if warn:
        print("════════ BEFORE YOU STOP ════════")
        for w in warn:
            print(w)
        print("═════════════════════════════════")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
