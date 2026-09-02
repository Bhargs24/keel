"""PreToolUse gate: block a Write/Edit whose incoming content carries a secret.

Reads the hook payload from stdin (Claude Code passes the tool call as JSON)
and scans the content that is ABOUT to be written -- not the working tree,
which at PreToolUse time still shows the world before the write. Exit code 2
is the blocking signal; anything printed to stderr goes back to the model so
it can fix the write instead of retrying it blind.

Stdlib only, cross-platform.
"""

from __future__ import annotations

import json
import re
import sys

_SECRET = re.compile(
    r"(?i)(api[_-]?key|secret|passwd|password|token|BEGIN [A-Z ]*PRIVATE KEY)"
    r"\s*[:=]\s*[\"'][^\"']{12,}"
)
#: Lines that declare an example/placeholder are not leaks.
_ALLOWED = re.compile(r"(?i)(example|placeholder|your[_-]|<[^>]+>|x{6,}|\*{4,})")


def scan(text: str) -> list[str]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if _SECRET.search(line) and not _ALLOWED.search(line):
            hits.append(f"  line {i}: {line.strip()[:88]}")
    return hits


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0  # no payload, nothing to scan
    tool_input = payload.get("tool_input") or {}
    candidates = [
        tool_input.get("content") or "",
        tool_input.get("new_string") or "",
    ]
    hits = [h for c in candidates for h in scan(c)]
    if hits:
        print("BLOCKED: this write looks like it carries a secret:", file=sys.stderr)
        print("\n".join(hits[:5]), file=sys.stderr)
        print(
            "Use the secret manager / an environment variable instead.\n"
            "See docs/00-RULES/CODE-RULEBOOK.md section 5.",
            file=sys.stderr,
        )
        return 2  # exit 2 is what actually blocks the tool call
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
