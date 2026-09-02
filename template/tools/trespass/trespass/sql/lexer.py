"""A small hand-written tokenizer for the Postgres DDL fragment we analyze.

Deliberately dependency-free and forgiving: it understands string literals with
``''`` escapes, dollar-quoted strings, line and block comments, quoted
identifiers, numbers, the operators that appear in policies, and everything else
as a bare word. Anything exotic still tokenizes; the parser decides what it can
make sense of.
"""

from __future__ import annotations

from dataclasses import dataclass

# Punctuation that is always a single-character token, never part of an operator.
_STRUCTURAL = "(),;.[]"

# Characters an operator token may be built from. Any maximal run of these is
# one operator -- so `||`, `@>`, `?|`, `#>>` and friends tokenize instead of
# crashing the lexer, and the parser decides what it can model.
_OPCHARS = frozenset("+-*/<>=~!@#%^&|?:$")

# Postgres's trailing-sign rule: a multi-char operator may end in `+` or `-`
# only if it also contains one of these. Otherwise the sign starts the next
# token (`a=-1` is `=` then `-1`, but `@-` stays one operator).
_SIGN_KEEPERS = frozenset("~!@#%^&|?")

_KEYWORDS = {
    "create", "table", "policy", "on", "as", "permissive", "restrictive",
    "for", "all", "select", "insert", "update", "delete", "to", "using",
    "with", "check", "alter", "enable", "disable", "force", "no", "row",
    "level", "security", "grant", "revoke", "and", "or", "not", "null",
    "true", "false", "is", "in", "exists", "public", "if", "distinct", "from",
    "default", "constraint", "primary", "key", "foreign", "references",
    "unique", "add", "column",
}


@dataclass(frozen=True)
class Token:
    kind: str  # "kw" | "ident" | "str" | "num" | "op" | "eof"
    value: str
    pos: int


class LexError(ValueError):
    pass


def tokenize(sql: str) -> list[Token]:
    toks: list[Token] = []
    i, n = 0, len(sql)
    while i < n:
        c = sql[i]
        # whitespace
        if c.isspace():
            i += 1
            continue
        # line comment
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            i = n if j == -1 else j + 1
            continue
        # block comment (nesting supported, as Postgres does)
        if sql.startswith("/*", i):
            depth, i = 1, i + 2
            while i < n and depth:
                if sql.startswith("/*", i):
                    depth, i = depth + 1, i + 2
                elif sql.startswith("*/", i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
            continue
        # dollar-quoted string: $tag$ ... $tag$ (tag must look like an
        # identifier, so a positional parameter such as `$1` is not mistaken
        # for the start of a string and swallowed up to the next `$`)
        if c == "$":
            end_tag = sql.find("$", i + 1)
            if end_tag != -1 and _is_dollar_tag(sql[i + 1 : end_tag]):
                tag = sql[i : end_tag + 1]
                close = sql.find(tag, end_tag + 1)
                if close != -1:
                    toks.append(Token("str", sql[end_tag + 1 : close], i))
                    i = close + len(tag)
                    continue
        # single-quoted string with '' escape
        if c == "'":
            j, buf = i + 1, []
            while j < n:
                if sql[j] == "'":
                    if j + 1 < n and sql[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(sql[j])
                j += 1
            if j >= n:
                raise LexError(f"unterminated string at {i}")
            toks.append(Token("str", "".join(buf), i))
            i = j + 1
            continue
        # quoted identifier
        if c == '"':
            j = i + 1
            while j < n and sql[j] != '"':
                j += 1
            if j >= n:
                raise LexError(f"unterminated identifier at {i}")
            toks.append(Token("ident", sql[i + 1 : j], i))
            i = j + 1
            continue
        # number
        if c.isdigit() or (c == "." and i + 1 < n and sql[i + 1].isdigit()):
            j = i
            while j < n and (sql[j].isdigit() or sql[j] in ".eE+-"):
                # stop a trailing +/- that is not part of an exponent
                if sql[j] in "+-" and sql[j - 1] not in "eE":
                    break
                j += 1
            toks.append(Token("num", sql[i:j], i))
            i = j
            continue
        # identifier / keyword
        if c.isalpha() or c == "_":
            j = i
            while j < n and (sql[j].isalnum() or sql[j] in "_$"):
                j += 1
            word = sql[i:j]
            kind = "kw" if word.lower() in _KEYWORDS else "ident"
            toks.append(Token(kind, word, i))
            i = j
            continue
        # structural punctuation: one character, one token
        if c in _STRUCTURAL:
            toks.append(Token("op", c, i))
            i += 1
            continue
        # operator: a maximal run of operator characters, Postgres-style
        if c in _OPCHARS:
            j = i
            while j < n and sql[j] in _OPCHARS:
                j += 1
            run = sql[i:j]
            # a comment marker inside the run ends the operator before it
            for marker in ("--", "/*"):
                k = run.find(marker)
                if k > 0:
                    run = run[:k]
            if not any(ch in _SIGN_KEEPERS for ch in run):
                while len(run) > 1 and run[-1] in "+-":
                    run = run[:-1]
            toks.append(Token("op", run, i))
            i += len(run)
            continue
        raise LexError(f"unexpected character {c!r} at {i}")
    toks.append(Token("eof", "", n))
    return toks


def _is_dollar_tag(body: str) -> bool:
    """Whether the text between two ``$`` signs is a valid dollar-quote tag."""
    if body == "":
        return True
    return (body[0].isalpha() or body[0] == "_") and all(
        ch.isalnum() or ch == "_" for ch in body
    )
