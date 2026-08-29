"""Command-line entry point.

    trespass check schema.sql
    trespass check migrations/ --intent trespass.intent
    cat schema.sql | trespass check -
    trespass check schema.sql --format sarif > trespass.sarif

Exit status is designed for CI: non-zero when something is proved vulnerable, so
a broken authorization policy fails the build.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from pathlib import Path

from . import __version__
from .analyze import analyze
from .findings import Report
from .intent import Intent, infer_intent, load_intent
from .report import render_json, render_sarif, render_terminal
from .schema import build_schema
from .sql.lexer import LexError
from .sql.parser import ParseError

_SQL_GLOB = "*.sql"


def main(argv: list[str] | None = None) -> int:
    # Best-effort: make Unicode output work even on a legacy Windows code page.
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return _cmd_check(args)
    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trespass",
        description="Prove your tenants can't read each other's data.",
    )
    p.add_argument("--version", action="version", version=f"trespass {__version__}")
    sub = p.add_subparsers(dest="command")

    c = sub.add_parser("check", help="analyze schema files for broken access control")
    c.add_argument("paths", nargs="+", help="one or more .sql files or directories, or - for stdin")
    c.add_argument("--intent", metavar="FILE", help="intent file (default: auto-discover trespass.intent)")
    c.add_argument("--format", choices=("terminal", "json", "sarif"), default="terminal")
    c.add_argument("--json", action="store_const", dest="format", const="json", help="shorthand for --format json")
    c.add_argument("--sarif", action="store_const", dest="format", const="sarif", help="shorthand for --format sarif")
    c.add_argument("--verbose", "-v", action="store_true", help="also show tables proved isolated")
    c.add_argument("--no-color", action="store_true", help="disable ANSI color")
    c.add_argument(
        "--no-default-grants",
        action="store_true",
        help="do not assume Supabase's default anon/authenticated grants; "
        "rely only on GRANTs written in the files",
    )
    c.add_argument(
        "--fail-on",
        choices=("vulnerable", "unknown", "never"),
        default="vulnerable",
        help="exit non-zero when a finding at or above this level exists (default: vulnerable)",
    )
    return p


def _cmd_check(args: argparse.Namespace) -> int:
    try:
        sql, source_name = _read_sources(args.paths)
    except FileNotFoundError as exc:
        print(f"trespass: {exc}", file=sys.stderr)
        return 2
    if not sql.strip():
        print("trespass: no SQL found in the given paths", file=sys.stderr)
        return 2

    try:
        intent = _resolve_intent(args, args.paths)
        report = analyze(
            sql, intent, assume_default_grants=not args.no_default_grants
        )
    except (ParseError, LexError) as exc:
        print(f"trespass: could not parse SQL: {exc}", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError) as exc:
        print(f"trespass: {exc}", file=sys.stderr)
        return 2

    _emit(report, args, source_name)
    return _exit_code(report, args.fail_on)


def _read_sources(paths: list[str]) -> tuple[str, str]:
    if paths == ["-"]:
        return sys.stdin.read(), "stdin"
    chunks: list[str] = []
    names: list[str] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            raise FileNotFoundError(f"no such file or directory: {raw}")
        files = sorted(path.rglob(_SQL_GLOB)) if path.is_dir() else [path]
        for file in files:
            chunks.append(file.read_text(encoding="utf-8"))
            names.append(file.name)
    return "\n".join(chunks), (names[0] if len(names) == 1 else f"{len(names)} files")


def _resolve_intent(args: argparse.Namespace, paths: list[str]) -> Intent | None:
    if args.intent:
        return load_intent(args.intent)
    # Auto-discover: trespass.intent in the cwd or beside the first path.
    candidates = [Path("trespass.intent")]
    first = Path(paths[0])
    if first.exists():
        base = first if first.is_dir() else first.parent
        candidates.append(base / "trespass.intent")
    for cand in candidates:
        if cand.is_file():
            return load_intent(cand)
    return None  # analyze() will infer


def _emit(report: Report, args: argparse.Namespace, source_name: str) -> None:
    if args.format == "json":
        print(render_json(report))
    elif args.format == "sarif":
        print(render_sarif(report, source_file=source_name))
    else:
        color = _use_color(args.no_color)
        print(
            render_terminal(
                report,
                color=color,
                verbose=args.verbose,
                ascii_only=not _supports_unicode(),
            )
        )


def _use_color(no_color_flag: bool) -> bool:
    if no_color_flag or os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or ""
    try:
        "✓✗─".encode(enc)
        return True
    except (LookupError, UnicodeEncodeError):
        return False


def _exit_code(report: Report, fail_on: str) -> int:
    counts = report.counts()
    if fail_on == "never":
        return 0
    if counts["vulnerable"] > 0:
        return 1
    if fail_on == "unknown" and counts["unknown"] > 0:
        return 1
    return 0


# Re-exported so `python -m trespass` and tests can call the machinery directly.
__all__ = ["analyze", "build_schema", "infer_intent", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
