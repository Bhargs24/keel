#!/usr/bin/env python3
"""Install the kit into a repository.

    python install.py /path/to/your/repo

Copies the template in, asks who is on the team, wires the roster and the
ownership map, and installs the git hooks. Nothing is overwritten without
being told: existing files are skipped and listed at the end so you can merge
them yourself.

    python install.py /path/to/repo --force      overwrite existing files
    python install.py /path/to/repo --dry-run    show what would happen
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
TEMPLATE = KIT / "template"

# Files you are expected to fill in. Listed at the end so nobody forgets.
# Most of the spec/ set is written for you by the pipeline (/keel). These four
# are the ones you (and Claude) shape by hand as the project takes form.
FILL_IN = [
    ("CLAUDE.md", "what you are building + the invariants (the pipeline fills most of it)"),
    ("docs/00-RULES/THE-RULEBOOK.md", "Parts 3 and 4: your judgement rules, and what has no undo"),
    ("docs/20-WORK/OWNERSHIP.map", "the real paths, once /architect has named them"),
    ("Makefile", "lint, typecheck, test and gen for the stack /architect chooses"),
]


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    got = input(f"{prompt}{suffix}: ").strip()
    return got or default


def collect_people() -> list[dict]:
    print("\nWho is on the team? The key becomes their branch prefix and their")
    print("ownership role, so keep it short and lowercase. Blank name to finish.\n")
    people = []
    while True:
        key = ask(f"  person {len(people)+1} key (e.g. alex)").lower()
        if not key:
            break
        people.append({
            "key": key,
            "display": ask("    display name", key.title()),
            "role": ask("    role", "developer"),
            "owns": ask("    owns (free text, for humans)", ""),
        })
    if not people:
        print("  no people given, keeping the example roster.")
    return people


def write_roster(root: Path, people: list[dict], dry: bool, force: bool):
    if not people:
        return
    lines = [
        "# The roster. Adding a person is adding a block: no code change.",
        "# The key is also the branch prefix and the ownership role.",
        "",
    ]
    for p in people:
        lines += [f"[people.{p['key']}]",
                  f'display = "{p["display"]}"',
                  f'role    = "{p["role"]}"',
                  f'owns    = "{p["owns"]}"', ""]
    target = root / "tracker" / "people.toml"
    if target.exists() and not force:
        print(f"  roster: tracker/people.toml already exists, left alone "
              f"(--force to replace with: {', '.join(p['key'] for p in people)})")
        return
    print(f"  roster: {', '.join(p['key'] for p in people)}")
    if not dry:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines), encoding="utf-8")


def write_map(root: Path, people: list[dict], dry: bool, force: bool):
    """Start the map with only the rules that are true on day one."""
    if not people:
        return
    target = root / "docs" / "20-WORK" / "OWNERSHIP.map"
    if target.exists() and not force:
        print("  ownership map: docs/20-WORK/OWNERSHIP.map already exists, left alone")
        return
    owner = people[0]["key"].upper()
    lines = [
        "# Ownership map * read by tools/ownership_check.py",
        "#",
        "#   <PERSON>    from tracker/people.toml, upper-cased",
        "#   SHARED      anyone may change it",
        "#   GENERATED   nobody hand-edits it, ever",
        "#",
        "# Longest matching prefix wins, so a subdirectory can belong to someone",
        "# else than its parent. Use that: it is how an ownership split becomes",
        "# visible in the directory tree, which is the only way it can be checked.",
        "#",
        "# Add real paths as they appear. An unmapped path defaults to SHARED, so",
        "# this never blocks genuinely new work.",
        "",
        f"tools                                {owner}",
        f".github                              {owner}",
        f"Makefile                             {owner}",
        "",
        "docs                                 SHARED",
        "tracker                              SHARED",
        "README.md                            SHARED",
        "CLAUDE.md                            SHARED",
        "docs/10-STATUS/NOW.md                SHARED",
        "",
    ]
    if not dry:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines), encoding="utf-8")


def copy_tree(root: Path, force: bool, dry: bool) -> tuple[int, list[str]]:
    copied, skipped = 0, []
    for src in sorted(TEMPLATE.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE)
        dst = root / rel
        if dst.exists() and not force:
            skipped.append(str(rel))
            continue
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied += 1
    return copied, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="the repository to install into")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = Path(a.target).expanduser().resolve()
    if not root.exists():
        sys.exit(f"no such directory: {root}")
    if not (root / ".git").exists():
        print(f"warning: {root} is not a git repository. The hooks and the")
        print("ownership check need git. Run `git init` first if that is a mistake.\n")

    print(f"Installing into {root}")
    if a.dry_run:
        print("(dry run: nothing will be written)\n")

    people = collect_people() if not a.dry_run else []
    copied, skipped = copy_tree(root, a.force, a.dry_run)
    write_roster(root, people, a.dry_run, a.force)
    write_map(root, people, a.dry_run, a.force)

    if not a.dry_run:
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                       cwd=root, capture_output=True)

    print(f"\n  {copied} files installed")
    if skipped:
        print(f"  {len(skipped)} left alone because they already exist:")
        for s in skipped[:12]:
            print(f"      {s}")
        if len(skipped) > 12:
            print(f"      ... and {len(skipped)-12} more")
        print("  Re-run with --force to overwrite, or merge them by hand.")

    print("\nFill these in before you rely on them:")
    for path, what in FILL_IN:
        print(f"  {path:<38} {what}")

    print("""
Now open your AI coding tool inside this repo and give it your idea:

  /keel "a booking tool for pet groomers that stops double-booking"

Keel takes it from there -- the business case, the product spec, the
architecture, a feasibility audit, then the build. Approve each step.

Already have a spec? Drop it in spec/ and skip to the build:
  /plan         load the build roadmap into the tracker
  /work         it decides what to build next
  /wrap         close the session cleanly

The three to remember:  /start when you sit down * /next to decide what's
next * /wrap when you stop.

New here? Read docs/01-INDUCTION/START-HERE.md -- it's written for anyone.
Nobody has to read the rulebook; Claude reads it for you.
""")


if __name__ == "__main__":
    main()
