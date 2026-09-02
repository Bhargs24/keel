"""Re-vendor trespass from its canonical checkout, and record the pin.

Keel ships a copy of trespass (github.com/Bhargs24/trespass) so a scaffolded
project can prove its row-level security with zero installs. A copy that can
drift silently is worse than a dependency, so the rules are:

* this script is the only way the copy changes;
* VENDORED.md records exactly which version and commit the copy came from;
* the test suite fails if the copy's __version__ disagrees with the pin.

Usage:
    python scripts/vendor_trespass.py <path-to-trespass-checkout>
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

KEEL_ROOT = Path(__file__).resolve().parents[1]
DEST = KEEL_ROOT / "template" / "tools" / "trespass"

#: Files keel adds on top of the upstream tree; never deleted by a sync.
KEEL_OWNED = {"run.py", "conftest.py", "README.md", "VENDORED.md"}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = Path(sys.argv[1]).resolve()
    pkg = src / "src" / "trespass"
    if not pkg.is_dir():
        print(f"error: {src} does not look like a trespass checkout "
              "(no src/trespass/)", file=sys.stderr)
        return 2

    commit = subprocess.check_output(
        ["git", "-C", str(src), "rev-parse", "--short", "HEAD"], text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "-C", str(src), "status", "--porcelain"], text=True
    ).strip()
    if dirty:
        print("error: the trespass checkout has uncommitted changes; "
              "vendor only from a clean, pushed commit.", file=sys.stderr)
        return 2
    version_match = re.search(
        r'__version__ = "([^"]+)"', (pkg / "__init__.py").read_text(encoding="utf-8")
    )
    if not version_match:
        print("error: could not read upstream __version__", file=sys.stderr)
        return 2
    version = version_match.group(1)

    # Replace the vendored package, tests, and examples wholesale.
    for name in ("trespass", "tests", "examples"):
        target = DEST / name
        if target.exists():
            shutil.rmtree(target)
    shutil.copytree(pkg, DEST / "trespass",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(src / "tests", DEST / "tests",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(src / "examples", DEST / "examples")
    shutil.copy2(src / "LICENSE", DEST / "LICENSE")

    (DEST / "VENDORED.md").write_text(
        f"""# Vendored: trespass {version}

| | |
|---|---|
| Upstream | https://github.com/Bhargs24/trespass |
| Version | {version} |
| Commit | {commit} |
| Synced | {date.today().isoformat()} |
| License | MIT (see LICENSE in this directory) |

The canonical project lives upstream and is released on PyPI as
`trespass-rls`. This copy exists so a scaffolded Keel project can run its
row-level-security proof with zero installs, offline, forever.

To update it, from the keel repo root:

    python scripts/vendor_trespass.py <path-to-trespass-checkout>

Do not edit files under `trespass/`, `tests/`, or `examples/` by hand --
the next sync overwrites them. Keel-owned shims: {", ".join(sorted(KEEL_OWNED))}.
The test suite pins this copy: it fails if `trespass.__version__` disagrees
with the version recorded here.
""",
        encoding="utf-8",
    )
    print(f"vendored trespass {version} @ {commit} into {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
