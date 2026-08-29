"""A small hand-written tokenizer for the Postgres DDL fragment we analyze.

Deliberately dependency-free and forgiving: it understands string literals with
``''`` escapes, dollar-quoted strings, line and block comments, quoted
identifiers, numbers, the operators that appear in policies, and everything else
as a bare word. Anything exotic still tokenizes; the parser decides what it can
make sense of.
"""

from __future__ import annotations

from dataclasses import dataclass

# Multi-character operators, longest first so the scanner is greedy.
_OPERATORS = [
    "->>",
    "->",
    "::",
    "<>",
    "!=",
    "<=",
    ">=",
    "=",
    "<",
    ">",
    "(",
    ")",
    ",",
    ";",
    ".",
    "+",
    "-",
    "*",
    "/",
    "%",
    "[",
    "]",
]

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
        # dollar-quoted string: $tag$ ... $tag$
        if c == "$":
            end_tag = sql.find("$", i + 1)
            if end_tag != -1:
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
        # operators / punctuation
        for op in _OPERATORS:
            if sql.startswith(op, i):
                toks.append(Token("op", op, i))
                i += len(op)
                break
        else:
            raise LexError(f"unexpected character {c!r} at {i}")
    toks.append(Token("eof", "", n))
    return toks
