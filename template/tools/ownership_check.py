#!/usr/bin/env python3
"""Fail a change that reaches into the other role's area without a crossing note.

Two people work this repo through long-running AI sessions. A session that
"helpfully" fixes something in the other person's area produces a conflict
nobody asked for, and neither person can tell any more what is theirs. So the
boundary is checked, not just written down.

The role comes from the branch name, so it is self-declaring and needs no
GitHub API and no username mapping:

    <person>/<TASK-ID>-<slug>     e.g.  alex/API-004-rate-limiter

Rules, in full:

  * A file owned by you                  -> allowed.
  * A file marked SHARED                 -> allowed.
  * A file marked GENERATED              -> never allowed by hand, any role.
  * A file owned by the other person     -> allowed ONLY if this change also
                                            adds a crossing note under
                                            docs/20-WORK/crossings/ that names
                                            the path.

Usage:  python tools/ownership_check.py [base-ref]
        base-ref defaults to origin/main.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "docs" / "20-WORK" / "OWNERSHIP.map"
CROSSINGS = "docs/20-WORK/crossings/"
def roles():
    """Role names are the keys in tracker/people.toml, upper-cased.
    Adding a person is adding a block there: no code change."""
    people = ROOT / "tracker" / "people.toml"
    if not people.exists():
        return ()
    return tuple(m.group(1).upper() for m in
                 re.finditer(r"^\[people\.([A-Za-z0-9_-]+)\]", 
                             people.read_text(encoding="utf-8"), re.M))


ROLES = roles()


def sh(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def load_map():
    """Longest prefix wins, so sort by descending prefix length."""
    rules = []
    for line in MAP.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            sys.exit(f"OWNERSHIP.map: cannot parse line: {line!r}")
        prefix, owner = parts
        if owner not in ROLES + ("SHARED", "GENERATED"):
            sys.exit(f"OWNERSHIP.map: unknown owner {owner!r} for {prefix!r}")
        rules.append((prefix.replace("\\", "/"), owner))
    rules.sort(key=lambda r: len(r[0]), reverse=True)
    return rules


def owner_of(path, rules):
    for prefix, owner in rules:
        if path == prefix or path.startswith(prefix.rstrip("/") + "/"):
            return owner
    return "SHARED"  # unmapped new top-level paths are shared until claimed


def role_from_branch(branch):
    m = re.match(r"^([A-Za-z0-9_-]+)/", branch, re.I)
    if not m:
        return None
    role = m.group(1).upper()
    return role if role in ROLES else None


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD")

    if branch in ("main", "HEAD", ""):
        print("ownership: on main or detached, nothing to check.")
        return 0

    role = role_from_branch(branch)
    if role is None:
        print(f"FAIL  branch {branch!r} does not declare a role.")
        print("      Name branches  <person>/<TASK-ID>-<slug>, where <person> is a key")
        print(f"      in tracker/people.toml. Known: {', '.join(r.lower() for r in ROLES) or 'none'}")
        print("      The name is how the boundary is checked. See")
        print("      docs/00-RULES/OWNERSHIP-PROTOCOL.md")
        return 1

    merge_base = sh("git", "merge-base", base, "HEAD") or base
    changed = [f for f in sh("git", "diff", "--name-only", merge_base, "HEAD").splitlines() if f]
    if not changed:
        print("ownership: no changed files.")
        return 0

    rules = load_map()
    notes = [f for f in changed if f.startswith(CROSSINGS)]
    declared = ""
    for n in notes:
        p = ROOT / n
        if p.exists():
            declared += p.read_text(encoding="utf-8", errors="ignore")

    generated, trespass = [], []
    for f in changed:
        own = owner_of(f, rules)
        if own == "GENERATED":
            generated.append(f)
        elif own in ROLES and own != role and f not in notes:
            if f not in declared:
                trespass.append((f, own))

    if generated:
        print("FAIL  generated files were hand-edited:")
        for f in generated:
            print(f"        {f}")
        print("      packages/shared is produced by `make gen` from the event")
        print("      schemas. Change the schema, regenerate, commit the result.")
        return 1

    if trespass:
        owners = sorted({own for _, own in trespass})
        print(f"FAIL  this is a {role} branch. "
              f"These files belong to {', '.join(owners)}:")
        for f, own in trespass:
            print(f"        {f}   [{own}]")
        print()
        print("      Preferred: do not change them. Ask the owner, who does it")
        print("      in their own branch. That is almost always faster than the")
        print("      merge you are about to cause.")
        print()
        print("      If it genuinely has to happen here, add a crossing note at")
        print(f"      {CROSSINGS}<date>-<slug>.md naming every path above,")
        print("      in this same change. The owner must approve the PR.")
        print("      Template and reasoning: docs/00-RULES/OWNERSHIP-PROTOCOL.md")
        return 1

    if notes:
        print(f"ownership: {role} ok, {len(notes)} declared crossing(s).")
    else:
        print(f"ownership: {role} ok, {len(changed)} file(s), no crossings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
