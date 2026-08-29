#!/usr/bin/env python3
"""Module boundary enforcement.

A monorepo without enforced boundaries rots into a monolith. This fails the
build when a module imports something it must not.

Rules (00-RULES/CODE-RULEBOOK.md 1.1):
    apps/*          may import  packages/*
    services/*      may import  packages/*
    packages/*      may import  packages/* (lower layers only)
    packages/shared may import  NOTHING internal

    no app imports another app
    no service imports another service's internals
    no circular dependencies

Run: make dep-check   (also runs in CI on every PR)
"""
from __future__ import annotations

import re

# Your module prefix: the Go module path, the npm scope, the Dart package
# prefix. Set these once and the boundary rules below work unchanged.
MODULE = "yourproject"
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# module -> what it is allowed to import from
ALLOWED: dict[str, set[str]] = {
    "apps": {"packages"},
    "services": {"packages"},
    "packages": {"packages"},
}

# packages/shared is generated and must stay dependency-free
LEAF_MODULES = {"packages/shared"}

IMPORT_PATTERNS = [
    # Go
    (r"\.go$", re.compile(rf'^\s*(?:[\w.]+\s+)?"({MODULE}/[^"]+)"', re.M)),
    # Python
    (r"\.py$", re.compile(r"^\s*(?:from|import)\s+((?:apps|services|packages)[\w.]*)", re.M)),
    # TypeScript / JavaScript
    (r"\.(ts|tsx|js|jsx)$", re.compile(r"""(?:from|require\()\s*['"](@{MODULE}/[^'"]+|(?:\.\./)+(?:apps|services|packages)/[^'"]+)['"]""", re.M)),
    # Dart
    (r"\.dart$", re.compile(r"""^\s*import\s+['"]package:({MODULE}_[\w]+)/""", re.M)),
]

SKIP_DIRS = {".git", "node_modules", ".dart_tool", "build", "dist", ".next",
             "__pycache__", "vendor", ".venv", "coverage", "target"}


def owning_module(path: Path) -> str | None:
    """Return 'apps/web', 'services/core-api', etc. for a file path."""
    try:
        rel = path.relative_to(ROOT).parts
    except ValueError:
        return None
    if len(rel) >= 2 and rel[0] in ("apps", "services", "packages"):
        return f"{rel[0]}/{rel[1]}"
    return None


def resolve_target(raw: str) -> str | None:
    """Map an import string to the module it refers to."""
    raw = raw.replace(f"@{MODULE}/", "packages/").replace(f"{MODULE}/", "")
    raw = raw.replace(f"{MODULE}_", "").lstrip("./")
    parts = re.split(r"[./]", raw)
    parts = [p for p in parts if p]
    if len(parts) >= 2 and parts[0] in ("apps", "services", "packages"):
        return f"{parts[0]}/{parts[1]}"
    return None


def scan() -> tuple[list[str], dict[str, set[str]]]:
    violations: list[str] = []
    graph: dict[str, set[str]] = defaultdict(set)

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
            continue
        src_mod = owning_module(path)
        if src_mod is None:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for suffix_re, pattern in IMPORT_PATTERNS:
            if not re.search(suffix_re, path.name):
                continue
            for raw in pattern.findall(text):
                raw = raw if isinstance(raw, str) else raw[0]
                dst_mod = resolve_target(raw)
                if dst_mod is None or dst_mod == src_mod:
                    continue

                graph[src_mod].add(dst_mod)
                src_layer, dst_layer = src_mod.split("/")[0], dst_mod.split("/")[0]
                rel = path.relative_to(ROOT)

                if src_mod in LEAF_MODULES:
                    violations.append(
                        f"{rel}: {src_mod} is GENERATED and must import nothing "
                        f"internal, but imports {dst_mod}")
                elif dst_layer not in ALLOWED.get(src_layer, set()):
                    violations.append(
                        f"{rel}: {src_layer}/* may not import {dst_layer}/* "
                        f"({src_mod} -> {dst_mod})")
                elif src_layer == dst_layer and src_layer in ("apps", "services"):
                    violations.append(
                        f"{rel}: no {src_layer[:-1]} may import another "
                        f"{src_layer[:-1]}'s internals ({src_mod} -> {dst_mod}). "
                        f"Talk over the API contract.")
    return violations, graph


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = defaultdict(int)

    def visit(node: str, stack: list[str]) -> None:
        colour[node] = GREY
        for nxt in sorted(graph.get(node, ())):
            if colour[nxt] == GREY:
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif colour[nxt] == WHITE:
                visit(nxt, stack + [nxt])
        colour[node] = BLACK

    for node in sorted(graph):
        if colour[node] == WHITE:
            visit(node, [node])
    return cycles


def main() -> int:
    violations, graph = scan()
    cycles = find_cycles(graph)

    if not violations and not cycles:
        n = sum(len(v) for v in graph.values())
        print(f"dep-check: OK. {len(graph)} modules, {n} internal edges, no violations.")
        return 0

    print("dep-check FAILED\n")
    for v in violations:
        print(f"  BOUNDARY  {v}")
    for c in cycles:
        print(f"  CYCLE     {' -> '.join(c)}")
    print(f"\n{len(violations)} boundary violation(s), {len(cycles)} cycle(s).")
    print("Rules: docs/00-RULES/CODE-RULEBOOK.md 1.1")
    return 1


if __name__ == "__main__":
    sys.exit(main())
