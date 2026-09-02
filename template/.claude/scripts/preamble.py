"""UserPromptSubmit: inject the rule preamble. Cross-platform stand-in for cat."""

import contextlib
import sys
from pathlib import Path

with contextlib.suppress(AttributeError, ValueError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print(
    (Path(__file__).resolve().parents[1] / "rule-preamble.txt").read_text(
        encoding="utf-8"
    )
)
