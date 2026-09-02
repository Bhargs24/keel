#!/usr/bin/env python3
"""Launcher for the vendored trespass analyzer (zero-dependency, stdlib only).

    python tools/trespass/run.py check supabase/migrations/ --intent app.intent

trespass proves whether one tenant can read another's data, or hands you the
exact query that shows they can. Wired into `make secure` and the /secure
command. Full docs: tools/trespass/README.md
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trespass.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
