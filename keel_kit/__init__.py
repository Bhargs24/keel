"""Keel: an open-source AI product builder.

Take an idea to a shipped, production-grade product. This CLI scaffolds a new
Keel project into a folder:

    pip install keel-kit
    keel init my-product
    cd my-product
    python tools/keel.py
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

__version__ = "0.2.0"


def _template_dir() -> Path:
    """The bundled project template, whether pip-installed or run from a checkout."""
    here = Path(__file__).resolve().parent
    for cand in (here / "template", here.parent / "template"):
        if (cand / "tools" / "keel.py").exists():
            return cand
    sys.exit("keel: could not find the bundled project template.")


def _copy_template(dst: Path) -> int:
    src = _template_dir()
    copied = 0
    for f in sorted(src.rglob("*")):
        if f.is_dir() or "__pycache__" in f.parts:
            continue
        target = dst / f.relative_to(src)
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        copied += 1
    return copied


def _git_user_name(cwd: Path) -> str:
    try:
        out = subprocess.run(["git", "config", "user.name"], cwd=cwd,
                             capture_output=True, text=True)
        return out.stdout.strip()
    except OSError:
        return ""


def _init(args: argparse.Namespace) -> int:
    dst = Path(args.target).expanduser().resolve()
    dst.mkdir(parents=True, exist_ok=True)
    n = _copy_template(dst)

    # The roster is generated, never copied: the template only ships an
    # example. Your name comes from --name, else your git identity, so the
    # tracker knows who you are from the very first command.
    roster = dst / "tracker" / "people.toml"
    if not roster.exists():
        name = (args.name or "").strip() or _git_user_name(dst) or "you"
        key = re.sub(r"[^a-z0-9]", "", name.lower()) or "you"
        roster.parent.mkdir(parents=True, exist_ok=True)
        roster.write_text(
            "# The roster. Add a person by adding a block -- see people.example.toml.\n"
            f'[people.{key}]\ndisplay = "{name.title()}"\nrole    = "founder"\nowns    = ""\n',
            encoding="utf-8")

    if not (dst / ".git").exists():
        subprocess.run(["git", "init"], cwd=dst, capture_output=True)
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                       cwd=dst, capture_output=True)

    print(f"\nKeel is set up in {dst}  ({n} files).\n")
    print("Open the guide. It shows you the next step, in plain English, all the")
    print("way from your idea to a shipped product:\n")
    print(f"    cd {dst}")
    print("    python tools/keel.py\n")
    print('Or open your AI coding tool in that folder and type:')
    print('    /keel "your idea in a sentence"\n')
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="keel", description=__doc__.split("\n")[0])
    p.add_argument("--version", action="version", version=f"keel {__version__}")
    sub = p.add_subparsers(dest="cmd")
    pi = sub.add_parser("init", help="scaffold a new Keel project into a folder")
    pi.add_argument("target", nargs="?", default=".",
                    help="the folder for your project (default: the current one)")
    pi.add_argument("--name", default="", help="your name, for the tracker roster")
    pi.set_defaults(func=_init)

    a = p.parse_args(argv)
    if not getattr(a, "func", None):
        p.print_help()
        return 0
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
