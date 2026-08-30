#!/usr/bin/env python3
"""Module boundary enforcement, config-driven and stack-agnostic.

A codebase without enforced boundaries rots into a monolith. This fails the build
when a module imports something the project's own boundary config forbids.

The rules are NOT hardcoded to any one project's layout. Each project declares its
module layout in `tools/boundaries.json`. With no such file, there are no
boundaries to enforce yet and this check passes cleanly, so it never misfires on a
project whose shape it does not know. `/architect` (or the scaffold step) writes
`boundaries.json` for the stack it chooses; a worked example ships alongside as
`tools/boundaries.example.json`.

Config shape (tools/boundaries.json):

    {
      "module": "acme",              // import prefix: Go module path, npm scope,
                                     // Dart package prefix. "" if none.
      "layers": {                    // a top-level dir that is a module layer ->
        "apps":     ["packages"],    // the layers it is allowed to import from
        "services": ["packages"],
        "packages": ["packages"]
      },
      "siblings_isolated": ["apps", "services"],  // no app imports another app, etc
      "leaf": ["packages/shared"]    // modules that must import nothing internal
    }

Run: python tools/dep_check.py     (also runs in CI on every PR)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "boundaries.json"

SKIP_DIRS = {".git", "node_modules", ".dart_tool", "build", "dist", ".next",
             "__pycache__", "vendor", ".venv", "coverage", "target"}


def load_config() -> dict | None:
    """The project's boundary rules, or None if it has not declared any yet."""
    if not CONFIG.exists():
        return None
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"dep-check: cannot read {CONFIG.name}: {e}")
        sys.exit(2)
    cfg.setdefault("module", "")
    cfg.setdefault("layers", {})
    cfg.setdefault("siblings_isolated", [])
    cfg.setdefault("leaf", [])
    if not cfg["layers"]:
        print(f"dep-check: {CONFIG.name} declares no layers; nothing to enforce.")
        return None
    return cfg


def owning_module(path: Path, layers: set[str]) -> str | None:
    """Return e.g. 'apps/web' for a file inside a declared layer, else None."""
    try:
        rel = path.relative_to(ROOT).parts
    except ValueError:
        return None
    if len(rel) >= 2 and rel[0] in layers:
        return f"{rel[0]}/{rel[1]}"
    return None


def import_patterns(module: str, layers: set[str]) -> list[tuple[str, re.Pattern]]:
    """Import matchers built from the project's own module prefix and layer names."""
    alt = "|".join(re.escape(l) for l in sorted(layers)) or r"(?!x)x"
    mod = re.escape(module) if module else r"(?!x)x"
    return [
        (r"\.go$", re.compile(rf'^\s*(?:[\w.]+\s+)?"({mod}/[^"]+)"', re.M)),
        (r"\.py$", re.compile(rf"^\s*(?:from|import)\s+((?:{alt})[\w.]*)", re.M)),
        (r"\.(ts|tsx|js|jsx)$",
         re.compile(rf"""(?:from|require\()\s*['"](@{mod}/[^'"]+|(?:\.\./)+(?:{alt})/[^'"]+)['"]""", re.M)),
        (r"\.dart$", re.compile(rf"""^\s*import\s+['"]package:({mod}_[\w]+)/""", re.M)),
    ]


def resolve_target(raw: str, module: str, layers: set[str]) -> str | None:
    """Map an import string to the 'layer/name' module it refers to, else None."""
    if module:
        raw = raw.replace(f"@{module}/", "packages/").replace(f"{module}/", "")
        raw = raw.replace(f"{module}_", "")
    raw = raw.lstrip("./")
    parts = [p for p in re.split(r"[./]", raw) if p]
    if len(parts) >= 2 and parts[0] in layers:
        return f"{parts[0]}/{parts[1]}"
    return None


def scan(cfg: dict) -> tuple[list[str], dict[str, set[str]]]:
    layers = set(cfg["layers"])
    allowed: dict[str, list[str]] = cfg["layers"]
    leaf = set(cfg["leaf"])
    isolated = set(cfg["siblings_isolated"])
    patterns = import_patterns(cfg["module"], layers)

    violations: list[str] = []
    graph: dict[str, set[str]] = defaultdict(set)

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
            continue
        src_mod = owning_module(path, layers)
        if src_mod is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for suffix_re, pattern in patterns:
            if not re.search(suffix_re, path.name):
                continue
            for raw in pattern.findall(text):
                raw = raw if isinstance(raw, str) else raw[0]
                dst_mod = resolve_target(raw, cfg["module"], layers)
                if dst_mod is None or dst_mod == src_mod:
                    continue

                graph[src_mod].add(dst_mod)
                src_layer, dst_layer = src_mod.split("/")[0], dst_mod.split("/")[0]
                rel = path.relative_to(ROOT)

                if src_mod in leaf:
                    violations.append(
                        f"{rel}: {src_mod} must import nothing internal, "
                        f"but imports {dst_mod}")
                elif dst_layer not in allowed.get(src_layer, []):
                    violations.append(
                        f"{rel}: {src_layer}/* may not import {dst_layer}/* "
                        f"({src_mod} -> {dst_mod})")
                elif src_layer == dst_layer and src_layer in isolated:
                    one = src_layer[:-1] if src_layer.endswith("s") else src_layer
                    violations.append(
                        f"{rel}: no {one} may import another {one}'s internals "
                        f"({src_mod} -> {dst_mod}). Talk over the contract.")
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
    cfg = load_config()
    if cfg is None:
        print("dep-check: no module boundaries configured "
              "(add tools/boundaries.json to enforce them); nothing to check.")
        return 0

    violations, graph = scan(cfg)
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
    print("Rules: tools/boundaries.json and docs/00-RULES/CODE-RULEBOOK.md 1.1")
    return 1


if __name__ == "__main__":
    sys.exit(main())
