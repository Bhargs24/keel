# Contributing

Thanks for looking. Keel is small on purpose and easy to hack on.

## Setup

```bash
pip install -e ".[dev]"
pytest && ruff check keel_kit tests scripts template
```

## The bar

Every change keeps four things true:

1. **The kit and the template run on the standard library.** No runtime
   dependencies, ever. Dev tools (pytest, ruff, z3) stay in `[dev]`.
2. **Claims are enforced or absent.** If the README says a gate fails the
   build, a test proves it fails the build. A check with nothing to check
   reports itself `inactive`, never "passed".
3. **The vendored trespass copy only changes through
   `scripts/vendor_trespass.py`.** It is pinned in
   `template/tools/trespass/VENDORED.md`; the test suite fails on drift.
   Fix trespass bugs upstream at github.com/Bhargs24/trespass, then re-vendor.
4. **Everything works on Windows.** Hooks and tools are Python, paths go
   through `pathlib`, output survives legacy code pages. If you must use a
   shell construct, it goes in a CI workflow, not in the template.

## Good first issues

- More `/design` and `/architect` prompt depth for specific stacks.
- A `track undo` for the last transition.
- Cockpit: a read-only history view of the tracker log.
