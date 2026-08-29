"""Authorization *intent* -- the piece no code scanner can recover on its own.

A row-level-security policy tells you what the database *enforces*. It cannot
tell you what the developer *meant*, and the gap between the two is where broken
access control lives. ``trespass`` closes that gap from two directions:

* **Declared intent** -- a short ``.intent`` file where you say, in plain terms,
  who owns each table and who may read or write it. This is the rigorous path,
  and it lets the tool return hard VULNERABLE / ISOLATED verdicts.

* **Inferred intent** -- when there is no file, a conservative guess from column
  names (``user_id`` looks owned; ``org_id`` looks tenant-scoped). This powers
  the instant "just point it at your schema" experience, and its findings are
  clearly marked as resting on a guess.

The file format is intentionally boring -- an INI parsed by the standard library,
so there is still nothing to ``pip install``.
"""

from __future__ import annotations

import configparser
from dataclasses import dataclass, field
from pathlib import Path

from .encode import SESSION_UID
from .schema import Schema
from .smt import Func, Lit, Term

# Access levels a command can be given.
OWNER = "owner"
PUBLIC = "public"
AUTHENTICATED = "authenticated"
NOBODY = "nobody"
_LEVELS = {OWNER, PUBLIC, AUTHENTICATED, NOBODY}

_COMMANDS = ("select", "insert", "update", "delete")

# Column names that strongly imply per-user ownership (identity = auth.uid()).
_OWNER_COLUMNS = {
    "user_id", "owner_id", "author_id", "created_by", "uid", "profile_id",
    "customer_id", "seller_id", "sender_id", "account_owner",
}
# Column names that imply tenant/organization scoping (identity = a JWT claim).
_TENANT_COLUMNS = {
    "org_id", "organization_id", "tenant_id", "team_id", "workspace_id",
    "company_id", "account_id",
}


@dataclass
class TableIntent:
    tenant: str | None  # the column that says who a row belongs to
    identity_kind: str = "uid"  # "uid" | "claim"
    identity_claim: str | None = None  # when identity_kind == "claim"
    access: dict[str, str] = field(default_factory=dict)  # command -> level

    def level(self, command: str) -> str:
        if command in self.access:
            return self.access[command]
        # Sensible defaults: if we know who owns a row, assume owner-only.
        return OWNER if self.tenant else AUTHENTICATED

    def identity_term(self) -> Term:
        """The value a row's tenant column must equal for the caller to be its
        rightful owner: the caller's uid, or a claim from their JWT."""
        if self.identity_kind == "claim":
            return Func("json->>", (Func("auth.jwt", ()), Lit(self.identity_claim)))
        return SESSION_UID


@dataclass
class Intent:
    tables: dict[str, TableIntent] = field(default_factory=dict)
    source: str = "none"  # "declared" | "inferred"

    def for_table(self, name: str) -> TableIntent | None:
        return self.tables.get(name.lower())


def load_intent(path: str | Path) -> Intent:
    cfg = configparser.ConfigParser()
    cfg.optionxform = str  # type: ignore[method-assign,assignment]  # preserve key case
    read = cfg.read(path, encoding="utf-8")
    if not read:
        raise FileNotFoundError(f"intent file not found: {path}")
    intent = Intent(source="declared")
    for section in cfg.sections():
        opts = {k.lower(): v.strip() for k, v in cfg.items(section)}
        tenant = opts.get("tenant") or None
        identity_kind, claim = "uid", None
        raw_identity = opts.get("identity", "uid")
        if raw_identity.startswith("jwt:"):
            identity_kind, claim = "claim", raw_identity[4:]
        access: dict[str, str] = {}
        for cmd in _COMMANDS:
            if cmd in opts:
                level = opts[cmd].lower()
                if level not in _LEVELS:
                    raise ValueError(
                        f"[{section}] {cmd} = {level!r}: expected one of {sorted(_LEVELS)}"
                    )
                access[cmd] = level
        intent.tables[section.lower()] = TableIntent(
            tenant=tenant, identity_kind=identity_kind, identity_claim=claim, access=access
        )
    return intent


def infer_intent(schema: Schema) -> Intent:
    """Guess intent from column names. Conservative on purpose: findings built on
    an inference are reported as such and never as a hard proof of a bug."""
    intent = Intent(source="inferred")
    for name, table in schema.tables.items():
        cols = set(table.columns)
        owner_col = next((c for c in _OWNER_COLUMNS if c in cols), None)
        tenant_col = next((c for c in _TENANT_COLUMNS if c in cols), None)
        if owner_col:
            intent.tables[name] = TableIntent(tenant=owner_col, identity_kind="uid")
        elif tenant_col:
            intent.tables[name] = TableIntent(
                tenant=tenant_col, identity_kind="claim", identity_claim=tenant_col
            )
    return intent
