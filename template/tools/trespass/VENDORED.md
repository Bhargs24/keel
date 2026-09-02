# Vendored: trespass 0.2.0

| | |
|---|---|
| Upstream | https://github.com/Bhargs24/trespass |
| Version | 0.2.0 |
| Commit | e62cc99 |
| Synced | 2026-09-02 |
| License | MIT (see LICENSE in this directory) |

The canonical project lives upstream and is released on PyPI as
`trespass-rls`. This copy exists so a scaffolded Keel project can run its
row-level-security proof with zero installs, offline, forever.

To update it, from the keel repo root:

    python scripts/vendor_trespass.py <path-to-trespass-checkout>

Do not edit files under `trespass/`, `tests/`, or `examples/` by hand --
the next sync overwrites them. Keel-owned shims: README.md, VENDORED.md, conftest.py, run.py.
The test suite pins this copy: it fails if `trespass.__version__` disagrees
with the version recorded here.
