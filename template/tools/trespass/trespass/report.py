"""Render a :class:`~trespass.findings.Report` for humans and for machines.

Three renderers, one report:

* ``terminal`` -- the default. Leads with the exploit, because a proof you can
  paste into ``psql`` is more convincing than any severity badge.
* ``json`` -- the whole report, for piping into other tools.
* ``sarif`` -- so findings show up inline on a GitHub pull request.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from .findings import Finding, Report, Verdict

# --------------------------------------------------------------------------- #
# ANSI helpers (no dependency on a color library).
# --------------------------------------------------------------------------- #
_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "grey": "\033[90m",
}
_VERDICT_STYLE = {
    Verdict.VULNERABLE: ("red", "✗ VULNERABLE", "X VULNERABLE"),
    Verdict.ISOLATED: ("green", "✓ ISOLATED", "OK ISOLATED"),
    Verdict.UNKNOWN: ("yellow", "? UNKNOWN", "? UNKNOWN"),
    Verdict.INFO: ("blue", "• INFO", "- INFO"),
}


def _c(text: str, *styles: str, color: bool) -> str:
    if not color:
        return text
    prefix = "".join(_CODES[s] for s in styles)
    return f"{prefix}{text}{_CODES['reset']}"


def render_terminal(
    report: Report, *, color: bool = True, verbose: bool = False, ascii_only: bool = False
) -> str:
    out: list[str] = []
    findings = report.sorted()
    shown = findings if verbose else [f for f in findings if f.verdict is not Verdict.ISOLATED]

    for f in shown:
        out.append(_render_finding(f, color=color, ascii_only=ascii_only))
        out.append("")

    out.append(_render_summary(report, color=color, ascii_only=ascii_only))
    return "\n".join(out)


def _render_finding(f: Finding, *, color: bool, ascii_only: bool = False) -> str:
    style, label_u, label_a = _VERDICT_STYLE[f.verdict]
    label = label_a if ascii_only else label_u
    lines: list[str] = []

    loc = f"{f.table}"
    if f.command:
        loc += f"  ·  {f.command.upper()}"
    if f.role:
        loc += f"  ·  role: {f.role}"
    lines.append("  " + _c(loc, "bold", color=color))
    lines.append(
        "  "
        + _c(label, style, "bold", color=color)
        + _c(f"  {f.severity.value}", "grey", color=color)
        + _c(f"   [{f.rule}]", "grey", color=color)
    )
    lines.append("")
    lines.append("  " + _wrap(f.title, 74, indent="  "))

    if f.policy_expr:
        lines.append("")
        lines.append("  " + _c("Your policy:", "dim", color=color))
        lines.append("      " + _c(f.policy_expr, "cyan", color=color))

    w = f.witness
    if w is not None:
        lines.append("")
        lines.append("  " + _c("Counterexample (from the solver):", "dim", color=color))
        for k, v in w.session.items():
            lines.append(f"      session  {k} = " + _c(v, "yellow", color=color))
        for k, v in w.row.items():
            val = f" = {v}" if v else ""
            lines.append(f"      row      {k}{val}")
        if w.precondition:
            lines.append("      " + _c(f"holds for {w.precondition}", "grey", color=color))
        lines.append("")
        lines.append("  " + _c("Reproduce it:", "dim", color=color))
        lines.append("      " + _c(w.query, "red" if f.verdict is Verdict.VULNERABLE else "yellow", color=color))
        lines.append("      " + _c(f"-- {w.effect}", "grey", color=color))

    if f.detail:
        lines.append("")
        lines.append("  " + _wrap(f.detail, 74, indent="  "))

    if f.fix:
        lines.append("")
        lines.append("  " + _c("Fix:", "green", "bold", color=color))
        for fl in f.fix.splitlines():
            lines.append("      " + _c(fl, "green", color=color))

    return "\n".join(lines)


def _render_summary(report: Report, *, color: bool, ascii_only: bool = False) -> str:
    counts = report.counts()
    bar = "  " + _c(("-" if ascii_only else "─") * 60, "grey", color=color)
    parts = [
        _plural(report.tables_analyzed, "table"),
        _plural(report.policies_analyzed, "policy", "policies"),
        _c(f"{counts['vulnerable']} vulnerable", "red", color=color) if counts["vulnerable"] else "0 vulnerable",
        _c(f"{counts['unknown']} unknown", "yellow", color=color) if counts["unknown"] else "0 unknown",
        _c(f"{counts['isolated']} proved isolated", "green", color=color) if counts["isolated"] else "0 proved",
    ]
    n = counts["vulnerable"]
    ways = "way" if n == 1 else "ways"
    verdict_line = (
        _c("  No proven holes. ", "green", "bold", color=color) + _c("Run with --verbose to see the proofs.", "grey", color=color)
        if report.ok
        else _c(f"  {n} proven {ways} for one user to reach another's data.", "red", "bold", color=color)
    )
    return "\n".join([bar, "  " + "  ·  ".join(parts), verdict_line])


def _wrap(text: str, width: int, *, indent: str) -> str:
    import textwrap

    return ("\n" + indent).join(textwrap.wrap(text, width)) or text


def _plural(n: int, word: str, plural: str | None = None) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {plural or word + 's'}"


# --------------------------------------------------------------------------- #
# Machine-readable.
# --------------------------------------------------------------------------- #
def render_json(report: Report) -> str:
    payload = {
        "tables_analyzed": report.tables_analyzed,
        "policies_analyzed": report.policies_analyzed,
        "counts": report.counts(),
        "ok": report.ok,
        "findings": [_finding_dict(f) for f in report.sorted()],
    }
    return json.dumps(payload, indent=2)


def _finding_dict(f: Finding) -> dict[str, object]:
    d = asdict(f)
    d["verdict"] = f.verdict.value
    d["severity"] = f.severity.value
    return d


_SARIF_LEVEL = {
    Verdict.VULNERABLE: "error",
    Verdict.UNKNOWN: "warning",
    Verdict.INFO: "note",
    Verdict.ISOLATED: "note",
}


def render_sarif(report: Report, *, source_file: str = "schema.sql") -> str:
    """A minimal but valid SARIF 2.1.0 log, so findings annotate a GitHub PR."""
    rules: dict[str, dict[str, object]] = {}
    results = []
    for f in report.sorted():
        if f.verdict is Verdict.ISOLATED:
            continue
        rules.setdefault(
            f.rule,
            {"id": f.rule, "name": f.rule, "shortDescription": {"text": f.title}},
        )
        results.append(
            {
                "ruleId": f.rule,
                "level": _SARIF_LEVEL[f.verdict],
                "message": {"text": f"{f.title}. {f.detail}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": source_file},
                            "region": {"startLine": 1},
                        }
                    }
                ],
                "properties": {
                    "table": f.table,
                    "command": f.command,
                    "role": f.role,
                    "verdict": f.verdict.value,
                    "severity": f.severity.value,
                    "exploit": f.witness.query if f.witness else None,
                },
            }
        )
    log = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "trespass",
                        "informationUri": "https://github.com/bhargavraghavendra/trespass",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(log, indent=2)


def summary_line(report: Report) -> str:
    c = report.counts()
    return (
        f"{c['vulnerable']} vulnerable, {c['unknown']} unknown, "
        f"{c['isolated']} isolated across {report.tables_analyzed} tables"
    )


def _severity_order(f: Finding) -> int:
    return -f.severity.rank
