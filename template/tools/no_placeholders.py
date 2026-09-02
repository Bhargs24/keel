#!/usr/bin/env python3
"""Fails the build on placeholder code.

00-RULES/DELIVERY-PROTOCOL.md section 1: every feature is production-grade and
complete on the first pass. No mocks, no stubs, no TODOs, no happy-path-only.

A genuine deferral is a work item with an ID, referenced as WORK-ITEM: <id>,
not a comment nobody will ever find.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNED = re.compile(
    r"\b(TODO|FIXME|XXX|HACK|for now|temporary|placeholder|dummy data|"
    r"not implemented|hardcoded|we'll fix|fix later|mock(?:ed)? data|stub(?:bed)?)\b",
    re.IGNORECASE,
)
# Accepts the tracker's own ID shapes: T-042, API-004, W1.8, SP-01 ...
ALLOW = re.compile(r"WORK-ITEM:\s*[A-Z]{1,8}[-.]?\d[\w.-]*", re.IGNORECASE)
SKIP_DIRS = {
    ".git",
    "node_modules",
    ".dart_tool",
    "build",
    "dist",
    ".next",
    "__pycache__",
    "vendor",
    ".venv",
    "coverage",
    "target",
    "tools",
    ".github",
    ".claude",
}
CODE = {".go", ".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".sql"}


def main() -> int:
    hits: list[str] = []
    for p in ROOT.rglob("*"):
        if (
            not p.is_file()
            or p.suffix not in CODE
            or any(d in p.parts for d in SKIP_DIRS)
        ):
            continue
        for n, line in enumerate(
            p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            if BANNED.search(line) and not ALLOW.search(line):
                hits.append(f"  {p.relative_to(ROOT)}:{n}: {line.strip()[:90]}")
    if hits:
        print("placeholder code found. Production-grade or not at all.\n")
        print("\n".join(hits))
        print(f"\n{len(hits)} occurrence(s). DELIVERY-PROTOCOL.md section 1.")
        print("A real deferral is a work item ID: // WORK-ITEM: W1.8 backfill engine")
        return 1
    print("no-placeholders: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
