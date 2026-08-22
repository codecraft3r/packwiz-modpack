#!/usr/bin/env python3
"""
validate_snbt.py — FTB SNBT validator
======================================

Validates Stringified NBT files (typically ``*.snbt``) against the grammar
documented at https://docs.feed-the-beast.com/mod-docs/mods/technical/SNBT/.

Highlights vs. vanilla SNBT:
* ``#`` line comments.
* Single- or double-quoted strings.
* Numbers with explicit type suffixes (b/B, s/S, l/L, f/F, d/D).
* Booleans ``true`` / ``false`` (unquoted — quoted is a String).
* Inline compound values: ``key: { ... }``, ``key: [ ... ]``.
* Multi-line compound/array values where commas are OPTIONAL between items
  placed on different lines; commas REQUIRED between items on the same line.
* Vanilla typed-array prefixes ``[B;``, ``[I;``, ``[L;`` accepted for
  backward compatibility (FTB's docs say FTB SNBT is "pretty much compatible"
  with vanilla).

What this validator does:
  * Confirms overall structural balance (every ``{``/``[`` is closed, every
    ``}``/``]`` has an opener).
  * Confirms every key in a compound object is followed by ``:`` and a value.
  * Confirms single-line multi-element sequences are comma-separated.
  * Confirms strings are properly quoted and escaped.
  * Confirms numbers have a valid form and (optional) type suffix.
  * Confirms identifiers (``true`` / ``false`` / ``∞`` / ``NaN``) are not
    accidentally quoted (which would make them strings, not booleans).
  * Reports precise ``file:line:col`` diagnostics for every issue.

What it does NOT do:
  * It does NOT check semantics — a key being the right type for a given
    mod's config schema is the mod's job.
  * It does NOT enforce any specific value range (e.g. ``Range: 0 ~ 100`` in
    comments is informational only).
  * It does NOT rewrite or "auto-fix" the file. Validation is read-only by
    design; we want CI / commit hooks to surface the exact source location.

Usage
-----
::

    # validate every .snbt file under a directory
    python scripts/validate_snbt.py config/

    # validate explicit files
    python scripts/validate_snbt.py config/ftbchunks-client.snbt \
                                       kubejs/foo.snbt

    # JSON report (for CI)
    python scripts/validate_snbt.py --format json config/

Exit codes:
  0   No issues.
  1   One or more validation errors found.
  2   Invocation error (bad args, unreadable file, etc.).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

__all__ = ["validate_file", "validate_text", "Diagnostic", "ValidationResult"]

# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

# A token carries its source text, the 1-based line/col where it starts, and
# whether it is followed by a newline (used to enforce the single-line
# comma rule).
TOK_LBRACE = "LBRACE"
TOK_RBRACE = "RBRACE"
TOK_LBRACKET = "LBRACKET"
TOK_RBRACKET = "RBRACKET"
TOK_COLON = "COLON"
TOK_COMMA = "COMMA"
TOK_STRING = "STRING"
TOK_NUMBER = "NUMBER"
TOK_IDENT = "IDENT"          # unquoted key, true, false, ∞, NaN
TOK_TYPED_ARRAY = "TYPED_ARRAY"  # [B; / [I; / [L;
TOK_EOF = "EOF"


@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int
    # The 1-based line/col where this token ENDS. The parser uses these
    # to decide whether two sibling tokens live on the same source line
    # (which triggers the single-line comma rule in arrays).
    end_line: int = 0
    end_col: int = 0


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


@dataclass
class Diagnostic:
    file: str
    line: int
    col: int
    end_line: int
    end_col: int
    code: str
    message: str

    def format(self, use_color: bool = True) -> str:
        path = self.file
        loc = f"{path}:{self.line}:{self.col}"
        if self.end_line != self.line or self.end_col != self.col:
            loc += f"-{self.end_line}:{self.end_col}"
        if use_color and sys.stderr.isatty():
            return f"\033[1;31m{loc}\033[0m: \033[1m{self.code}\033[0m: {self.message}"
        return f"{loc}: {self.code}: {self.message}"


@dataclass
class ValidationResult:
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.diagnostics

    def add(self, diag: Diagnostic) -> None:
        self.diagnostics.append(diag)


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

# Number pattern. The FTB grammar accepts:
#   <int>(b|B|s|S|l|L)?            -> byte / short / long
#   <float>(f|F|d|D)?              -> float / double (default)
#   <float>(e|E[+-]?<int>)(f|F|d|D)?
#   hex 0x... form is allowed by vanilla SNBT, so we accept it too.
# We allow an optional leading sign so that ``-128b`` and ``-1.5d`` parse.
_NUMBER_RE = re.compile(
    r"""
    (?P<sign> - )?
    (?:
        (?P<hex> 0x[0-9A-Fa-f]+ )
        |
        (?P<dec>
            (?P<int>\d+)
            (\. (?P<frac>\d+))?
            ([eE] (?P<exp>[+-]?\d+))?
            (?P<sfx>[bBsSlLdDfF])?
        )
    )
    """,
    re.VERBOSE,
)

# Identifiers allowed on the right-hand side of `key:` and as bare values
# (booleans, ∞, NaN, ±Infinity, NanF). The lexer accepts the signed
# infinity forms ``-∞`` / ``-Infinity`` as a single token so they don't
# fall through to the number rule.

# Identifiers allowed on the right-hand side of `key:` and as bare values
# (booleans, ∞, NaN). Identifiers with leading digits / special characters
# are NOT valid keys without quoting. Strings handle all other cases.
_IDENT_START = set(
    "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "\u221e\u00b0"  # ∞ (U+221E) and the legacy ° form some tools emit
)
_IDENT_CONT = _IDENT_START | set("0123456789-")

# Vanilla SNBT typed-array opener (e.g. `[I; 1, 2, 3]`).
_TYPED_ARRAY_KINDS = ("B", "I", "L")


def _iter_tokens(source: str) -> Iterator[Token]:
    """Yield tokens for ``source``. Raises ``LexError`` on lexical errors.

    Comments (``#`` through end-of-line) and whitespace are skipped
    silently. Inside strings, ``\\`` escapes the next character. ``;``
    shares its lexer branch with ``:`` — the parser distinguishes them
    via ``token.value``.
    """
    i = 0
    n = len(source)
    line = 1
    col = 1

    while i < n:
        ch = source[i]

        # Newline
        if ch == "\n":
            line += 1
            col = 1
            i += 1
            continue
        # Whitespace (incl. CR)
        if ch in " \t\r":
            i += 1
            col += 1
            continue
        # UTF-8 BOM (U+FEFF) at the start of a file. FTB's tooling is
        # tolerant of a leading BOM, so we are too. Skip a single BOM
        # at offset 0 and treat the rest of the file normally.
        if ch == "\ufeff" and i == 0:
            i += 1
            continue
        # Comment: # until newline (not including the newline)
        if ch == "#":
            j = source.find("\n", i)
            if j == -1:
                j = n
            i = j
            col = 1
            continue

        # Single-character tokens
        if ch == "{":
            yield Token(TOK_LBRACE, ch, line, col, line, col)
            i += 1
            col += 1
            continue
        if ch == "}":
            yield Token(TOK_RBRACE, ch, line, col, line, col)
            i += 1
            col += 1
            continue
        if ch == "[":
            yield Token(TOK_LBRACKET, ch, line, col, line, col)
            i += 1
            col += 1
            continue
        if ch == "]":
            yield Token(TOK_RBRACKET, ch, line, col, line, col)
            i += 1
            col += 1
            continue
        # `:` and `;` share a lexer branch — they both produce a COLON
        # token whose `value` distinguishes them. The parser uses
        # `value == ";"` to recognise typed-array prefixes like `[I;`.
        if ch in ":;":
            yield Token(TOK_COLON, ch, line, col, line, col)
            i += 1
            col += 1
            continue
        if ch == ",":
            yield Token(TOK_COMMA, ch, line, col, line, col)
            i += 1
            col += 1
            continue

        # String: "..." or '...' with backslash escapes
        if ch in "\"'":
            quote = ch
            start_line, start_col = line, col
            j = i + 1
            while j < n:
                c = source[j]
                if c == "\\":
                    j += 2
                    col += 2
                    continue
                if c == quote:
                    end_col = col + 1
                    yield Token(TOK_STRING, source[i : j + 1], start_line, start_col, line, end_col)
                    j += 1
                    col = end_col + 1
                    i = j
                    break
                if c == "\n":
                    raise LexError(
                        start_line,
                        start_col,
                        "unterminated string literal — closing quote never found before end of line",
                    )
                j += 1
                col += 1
            else:
                raise LexError(
                    start_line,
                    start_col,
                    "unterminated string literal at end of file",
                )
            continue

        # Number (including signed forms like ``-128b`` or ``-1.5d``)
        if ch.isdigit() or (
            ch == "-" and i + 1 < n and (source[i + 1].isdigit() or source[i + 1] == "0")
        ):
            start_line, start_col = line, col
            m = _NUMBER_RE.match(source, i)
            if not m or m.start() != i:
                raise LexError(
                    start_line,
                    start_col,
                    f"invalid number literal near {ch!r}",
                )
            text = m.group(0)
            # ``-0xFF`` is a legitimate hex literal in some SNBT dialects,
            # but vanilla SNBT only allows positive 0x... — reject it
            # with a clearer message so authors fix the typo.
            if m.group("hex") and m.group("sign"):
                raise LexError(
                    start_line,
                    start_col,
                    "hex literal may not have a leading sign; use a positive 0x... value",
                )
            end_col = col + len(text)
            yield Token(TOK_NUMBER, text, start_line, start_col, line, end_col)
            col = end_col
            i = m.end()
            continue

        # Special float forms ``∞``, ``-∞``, ``∞F``, ``-∞F`` (and the
        # legacy ``°`` variant) need to be lexed before they fall through
        # to either the number or identifier path — the leading ``-``
        # would otherwise be rejected by the number rule.
        if ch == "\u221e" or ch == "\u00b0":
            start_line, start_col = line, col
            j = i + 1
            # Optional ``F``/``f`` suffix for the float variants.
            if j < n and source[j] in "fF":
                j += 1
            text = source[i:j]
            end_col = col + len(text)
            yield Token(TOK_NUMBER, text, start_line, start_col, line, end_col)
            col = end_col
            i = j
            continue
        if ch == "-" and i + 1 < n and source[i + 1] in "\u221e\u00b0":
            start_line, start_col = line, col
            j = i + 2
            if j < n and source[j] in "fF":
                j += 1
            text = source[i:j]
            end_col = col + len(text)
            yield Token(TOK_NUMBER, text, start_line, start_col, line, end_col)
            col = end_col
            i = j
            continue

        # Identifier (key or bare identifier value)
        if ch in _IDENT_START:
            start_line, start_col = line, col
            j = i + 1
            while j < n and source[j] in _IDENT_CONT:
                j += 1
            text = source[i:j]
            end_col = col + len(text)
            yield Token(TOK_IDENT, text, start_line, start_col, line, end_col)
            col = end_col
            i = j
            continue

        # Anything else is a lexical error.
        raise LexError(line, col, f"unexpected character {ch!r}")

    yield Token(TOK_EOF, "", line, col, line, col)


class LexError(Exception):
    def __init__(self, line: int, col: int, message: str) -> None:
        self.line = line
        self.col = col
        self.message = message
        super().__init__(f"{line}:{col}: {message}")


# ---------------------------------------------------------------------------
# Parser / validator
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, tokens: list[Token], result: ValidationResult, file: str) -> None:
        self.tokens = tokens
        self.result = result
        self.file = file
        self.pos = 0

    # --- token cursor --------------------------------------------------------

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]  # EOF sentinel
        return self.tokens[idx]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.kind != TOK_EOF:
            self.pos += 1
        return tok

    def eat(self, kind: str, what: str) -> Token | None:
        tok = self.peek()
        if tok.kind != kind:
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "expected_token",
                    f"expected {what} ({kind!r}), got {tok.kind} {tok.value!r}",
                )
            )
            return None
        return self.advance()

    # --- top-level entry ------------------------------------------------------

    def parse_top(self) -> None:
        # A .snbt file's top level may be:
        #   * a single compound object, or
        #   * a sequence of values (vanilla SNBT root form).
        # FTB config files are always a compound, but we accept both.
        tok = self.peek()
        if tok.kind == TOK_EOF:
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "empty_file",
                    "file is empty; expected at least one value",
                )
            )
            return
        if tok.kind == TOK_LBRACE:
            self.parse_object_body(closer=TOK_RBRACE)
        elif tok.kind == TOK_LBRACKET:
            self.parse_array_body(closer=TOK_RBRACKET)
        else:
            self.parse_value()
        # Anything after EOF is a structural error.
        if self.peek().kind != TOK_EOF:
            tok = self.peek()
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "trailing_tokens",
                    f"unexpected {tok.kind} {tok.value!r} after end of structure",
                )
            )

    # --- object / array -----------------------------------------------------

    def parse_object_body(self, closer: str) -> None:
        """Consume ``{...}`` and validate every ``key: value`` pair.

        FTB's grammar allows items in a multi-line compound to be
        separated by newlines instead of commas; commas are only
        mandatory when two items appear on the same source line. The
        same exemption applies to arrays.
        """
        open_tok = self.advance()
        assert open_tok.kind == TOK_LBRACE
        seen_keys: set[str] = set()
        # Empty object is valid: `{}`.
        if self.peek().kind == closer:
            self.advance()
            return
        # State machine for the multi-line comma rule.
        #
        # FTB's grammar allows items in a multi-line compound to be
        # separated by newlines instead of commas; commas are only
        # mandatory when two items appear on the same source line.
        #
        # ``last_item_end_line`` is the source line where the previous
        # item (the value of the last parsed key:value pair) ended.
        # ``separator_kind`` records what, if anything, separated that
        # item from the next token. Allowed values:
        #
        #   None      -- no item has been parsed yet (first iteration)
        #   "none"    -- a value just ended, no comma has been seen
        #   "comma"   -- a comma was consumed between items
        #   "newline" -- the previous item ended on a different line
        #                than the next non-trivia token (newlines act
        #                as separators when items span lines)
        last_item_end_line: int | None = None
        separator_kind: str | None = None
        while True:
            tok = self.peek()
            if tok.kind == TOK_EOF:
                self.result.add(
                    Diagnostic(
                        self.file,
                        open_tok.line,
                        open_tok.col,
                        open_tok.end_line,
                        open_tok.end_col,
                        "unterminated_object",
                        f"object opened at {open_tok.line}:{open_tok.col} is missing closing '}}'",
                    )
                )
                return
            # The closing brace may appear at the top of the loop after
            # a trailing comma or whitespace; consume it and exit cleanly.
            if tok.kind == closer:
                self.advance()
                return

            # Update separator_kind based on what we know now.
            if last_item_end_line is not None:
                if separator_kind is None:
                    # First iteration after a value — if the next token
                    # is on a different line, treat the gap as a
                    # newline separator.
                    if tok.line != last_item_end_line:
                        separator_kind = "newline"
                    else:
                        separator_kind = "none"

            # Same-line check: a previous item on this line without a
            # separator between it and the next item is an error.
            if (
                separator_kind == "none"
                and tok.line == last_item_end_line
                and tok.kind not in (TOK_COMMA, TOK_RBRACE, TOK_RBRACKET, TOK_EOF)
            ):
                self.result.add(
                    Diagnostic(
                        self.file,
                        tok.line,
                        tok.col,
                        tok.end_line,
                        tok.end_col,
                        "missing_comma",
                        f"items on the same line must be separated by ',' "
                        f"(previous item ended at line {last_item_end_line})",
                    )
                )
                self._recover_to_closer(closer)
                return

            key_tok, key_str = self._read_key(seen_keys)
            if key_tok is None:
                self._recover_to_closer(closer)
                return

            colon = self.eat(TOK_COLON, "':' after key")
            if colon is None:
                self._recover_to_closer(closer)
                return

            # Empty value: next token is `}` / `,` / EOF without a value.
            if self.peek().kind in (TOK_RBRACE, TOK_COMMA, TOK_EOF):
                self.result.add(
                    Diagnostic(
                        self.file,
                        colon.line,
                        colon.col,
                        colon.end_line,
                        colon.end_col,
                        "missing_value",
                        f"key {key_str!r} has no value (expected a value after ':')",
                    )
                )
                if self.peek().kind == TOK_COMMA:
                    self.advance()
                self._recover_to_closer(closer)
                return

            value_tok = self.parse_value()
            if value_tok is None:
                self._recover_to_closer(closer)
                return

            nxt = self.peek()
            if nxt.kind == closer:
                self.advance()
                return
            if nxt.kind == TOK_COMMA:
                self.advance()
                # The next item starts after a comma — the same-line
                # check will be reset on the next iteration via
                # ``separator_kind``.
                last_item_end_line = value_tok.end_line
                separator_kind = "comma"
                continue
            # No comma and no closer. Reset to ``none`` so the next
            # iteration can decide between same-line (error) and
            # different-line (allowed).
            last_item_end_line = value_tok.end_line
            separator_kind = "none"
            # Loop; the top-of-loop check will inspect the next token.

    def parse_array_body(self, closer: str) -> None:
        # Peek first so we can route to the typed-array branch without
        # consuming the opener twice.
        first_tok = self.peek()
        # Vanilla SNBT typed array: ``[B; ...]``, ``[I; ...]``, ``[L; ...]``.
        # The lexer pre-pass ``_strip_typed_array_prefix`` collapses the
        # ``[``, ``I`` and ``;`` into a single TYPED_ARRAY token. The
        # following plain-array path consumes ``[`` via ``self.advance()``.
        if first_tok.kind == TOK_TYPED_ARRAY:
            open_tok = self.advance()  # consumes the ``[I;`` token
            kind = first_tok.value[1]
            assert kind in _TYPED_ARRAY_KINDS
            self._parse_typed_array_body(kind)
            if self.peek().kind == TOK_RBRACKET:
                self.advance()
                return
            self.result.add(
                Diagnostic(
                    self.file,
                    open_tok.line,
                    open_tok.col,
                    open_tok.end_line,
                    open_tok.end_col,
                    "unterminated_array",
                    f"array opened at {open_tok.line}:{open_tok.col} is missing closing ']'",
                )
            )
            return

        # Regular array: consume the ``[`` opener and proceed.
        open_tok = self.advance()
        assert open_tok.kind == TOK_LBRACKET

        # Empty array: `[]`.
        if self.peek().kind == TOK_RBRACKET:
            self.advance()
            return

        # Parse values. FTB allows multi-line arrays WITHOUT commas between
        # values that appear on different lines, but REQUIRES commas between
        # values that appear on the SAME line. The state machine mirrors
        # the one used by ``parse_object_body``:
        #
        #   separator_kind None  -- no value has been parsed yet
        #   separator_kind "none" -- a value just ended, no comma yet
        #   separator_kind "comma" -- a comma separated items on this line
        #   separator_kind "newline" -- the next token is on a new line
        prev_value_end_line: int | None = None
        prev_value_end_col: int | None = None
        separator_kind: str | None = None
        while True:
            tok = self.peek()
            if tok.kind == TOK_EOF:
                self.result.add(
                    Diagnostic(
                        self.file,
                        open_tok.line,
                        open_tok.col,
                        open_tok.end_line,
                        open_tok.end_col,
                        "unterminated_array",
                        f"array opened at {open_tok.line}:{open_tok.col} is missing closing ']'",
                    )
                )
                return

            # Decide what separator (if any) lies between the previous
            # value and this token.
            if prev_value_end_line is not None and separator_kind is None:
                if tok.line != prev_value_end_line:
                    separator_kind = "newline"
                else:
                    separator_kind = "none"

            # Same-line check: previous item on this line, no separator.
            if (
                separator_kind == "none"
                and tok.line == prev_value_end_line
                and tok.kind not in (TOK_COMMA, TOK_RBRACKET, TOK_EOF)
            ):
                self.result.add(
                    Diagnostic(
                        self.file,
                        tok.line,
                        tok.col,
                        tok.end_line,
                        tok.end_col,
                        "missing_comma",
                        f"values on the same line must be separated by ',' "
                        f"(previous value ended at line {prev_value_end_line}:col {prev_value_end_col})",
                    )
                )
                self._recover_to_closer(TOK_RBRACKET)
                return

            # If we see a comma here (between values), consume it and
            # continue with the next value.
            if tok.kind == TOK_COMMA:
                self.advance()
                nxt = self.peek()
                if nxt.kind in (TOK_RBRACKET, TOK_EOF):
                    self.result.add(
                        Diagnostic(
                            self.file,
                            tok.line,
                            tok.col,
                            tok.end_line,
                            tok.end_col,
                            "trailing_comma",
                            "trailing ',' with no following value",
                        )
                    )
                    if nxt.kind == TOK_RBRACKET:
                        self.advance()
                    return
                # Mark the comma so the same-line check on the next
                # iteration knows the separator is satisfied.
                separator_kind = "comma"
                continue

            if tok.kind == TOK_RBRACKET:
                self.advance()
                return

            value_tok = self.parse_value()
            if value_tok is None:
                self._recover_to_closer(TOK_RBRACKET)
                return
            prev_value_end_line = value_tok.end_line
            prev_value_end_col = value_tok.end_col
            separator_kind = "none"

    def _parse_typed_array_body(self, kind: str) -> None:
        # `[B;` / `[I;` allow byte/integer numbers; `[L;` allows string
        # class references (we accept any quoted string).
        if self.peek().kind == TOK_RBRACKET:
            # Empty typed array is allowed.
            return
        first = True
        while True:
            tok = self.peek()
            if tok.kind == TOK_EOF:
                return  # The caller surfaces the unterminated_array error.
            if tok.kind == TOK_RBRACKET:
                return
            if not first:
                if tok.kind == TOK_COMMA:
                    self.advance()
                    tok = self.peek()
                else:
                    # Missing comma between typed-array elements.
                    self.result.add(
                        Diagnostic(
                            self.file,
                            tok.line,
                            tok.col,
                            tok.end_line,
                            tok.end_col,
                            "missing_comma",
                            f"expected ',' between typed-array elements (got {tok.kind} {tok.value!r})",
                        )
                    )
                    self._recover_to_closer(TOK_RBRACKET)
                    return
            if kind == "L":
                if tok.kind != TOK_STRING:
                    self.result.add(
                        Diagnostic(
                            self.file,
                            tok.line,
                            tok.col,
                            tok.end_line,
                            tok.end_col,
                            "typed_array_element",
                            f"[L; ...] expects a string class reference, got {tok.kind} {tok.value!r}",
                        )
                    )
                    # Best-effort: keep going past it.
                    self.advance()
                    first = False
                    continue
                self.advance()
            else:
                if tok.kind != TOK_NUMBER:
                    self.result.add(
                        Diagnostic(
                            self.file,
                            tok.line,
                            tok.col,
                            tok.end_line,
                            tok.end_col,
                            "typed_array_element",
                            f"[{kind}; ...] expects a number, got {tok.kind} {tok.value!r}",
                        )
                    )
                    self.advance()
                    first = False
                    continue
                self.advance()
            first = False

    # --- keys / values ------------------------------------------------------

    def _read_key(self, seen: set[str]) -> tuple[Token | None, str]:
        tok = self.peek()
        key_str = ""
        if tok.kind == TOK_STRING:
            self.advance()
            key_str = tok.value
        elif tok.kind == TOK_IDENT:
            self.advance()
            key_str = tok.value
            # Quoted `"true"` / `"false"` are strings; bare `true` /
            # `false` as a KEY would be ambiguous and isn't supported by
            # the FTB examples. Allow it anyway — the parser will accept
            # the colon and parse the value normally.
        else:
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "invalid_key",
                    f"expected quoted string or unquoted identifier for object key, got {tok.kind} {tok.value!r}",
                )
            )
            return None, ""
        if key_str in seen:
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "duplicate_key",
                    f"duplicate key {key_str!r} in same object",
                )
            )
        seen.add(key_str)
        return tok, key_str

    def parse_value(self) -> Token | None:
        """Parse one value, returning its end-line/col or None on error."""
        tok = self.peek()
        if tok.kind == TOK_LBRACE:
            start = self.peek()
            self.parse_object_body(closer=TOK_RBRACE)
            return start  # end position is the closing `}` but we don't
            # track it precisely here; the caller uses line-col of the
            # opener for the single-line comma check, which is good
            # enough (it's the same line as the opener when on one line).
        if tok.kind == TOK_LBRACKET:
            start = self.peek()
            self.parse_array_body(closer=TOK_RBRACKET)
            return start
        if tok.kind == TOK_TYPED_ARRAY:
            # ``[I; 1, 2, 3]`` is a single value. ``parse_array_body``
            # has a typed-array branch that consumes the rest of the
            # prefix and the body when it sees a TYPED_ARRAY token, so
            # just dispatch to it directly. We return the opener token
            # so the same-line comma check works correctly when this
            # typed-array appears inside an outer array.
            start = self.peek()
            self.parse_array_body(closer=TOK_RBRACKET)
            return start
        if tok.kind in (TOK_STRING, TOK_NUMBER):
            self.advance()
            return tok
        if tok.kind == TOK_IDENT:
            v = tok.value
            if v in ("true", "false", "Infinity", "-Infinity", "NaN", "NanF"):
                # Plain boolean / special literal.
                self.advance()
                return tok
            # Some legacy / extended configs write `1f`/`0d` style without
            # an explicit number prefix; if the ident happens to start
            # with a digit, that's a lex error already. Pure identifiers
            # are not standalone values in FTB SNBT.
            self.result.add(
                Diagnostic(
                    self.file,
                    tok.line,
                    tok.col,
                    tok.end_line,
                    tok.end_col,
                    "invalid_value",
                    f"bare identifier {tok.value!r} is not a valid value "
                    f"(use a quoted string or a typed number suffix)",
                )
            )
            self.advance()
            return tok
        # Anything else (LBRACE/LBRACKET already handled; remaining are
        # punctuation and EOF). Report and stop.
        self.result.add(
            Diagnostic(
                self.file,
                tok.line,
                tok.col,
                tok.end_line,
                tok.end_col,
                "invalid_value",
                f"expected a value, got {tok.kind} {tok.value!r}",
            )
        )
        return None

    # --- recovery -----------------------------------------------------------

    def _recover_to_closer(self, closer: str) -> None:
        """Skip tokens until we hit `closer` (or EOF) to keep validating
        the rest of the file after an error."""
        depth = 0
        while True:
            tok = self.peek()
            if tok.kind == TOK_EOF:
                return
            if depth == 0 and tok.kind == closer:
                self.advance()
                return
            if tok.kind in (TOK_LBRACE, TOK_LBRACKET):
                depth += 1
            elif tok.kind in (TOK_RBRACE, TOK_RBRACKET):
                if depth == 0:
                    # Stray closer — just consume it and stop.
                    self.advance()
                    return
                depth -= 1
            self.advance()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _strip_typed_array_prefix(
    tokens: list[Token], result: ValidationResult, file: str
) -> list[Token]:
    """Pre-pass: merge ``[`` + IDENT(`B`|`I`|`L`) + ``;`` into a single
    TYPED_ARRAY token so the parser can handle it cleanly.

    Also reports ``typed_array_syntax`` when a ``[B``-style opener is
    seen WITHOUT a following semicolon — that's an authoring mistake
    we want to surface explicitly rather than letting the bare
    identifier fall through to the regular-array path.
    """
    out: list[Token] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.kind == TOK_LBRACKET:
            # [B; / [I; / [L;  — the well-formed case.
            if (
                i + 2 < len(tokens)
                and tokens[i + 1].kind == TOK_IDENT
                and tokens[i + 1].value in _TYPED_ARRAY_KINDS
                and tokens[i + 2].kind == TOK_COLON
                and tokens[i + 2].value == ";"
            ):
                new = Token(
                    TOK_TYPED_ARRAY,
                    f"[{tokens[i + 1].value};",
                    t.line,
                    t.col,
                    tokens[i + 2].end_line,
                    tokens[i + 2].end_col,
                )
                out.append(new)
                i += 3
                continue
            # [B / [I / [L  — missing semicolon. Emit a diagnostic and
            # let the regular-array path parse the body, where the bare
            # ``B``/``I``/``L`` identifier will fail as a value.
            if (
                i + 1 < len(tokens)
                and tokens[i + 1].kind == TOK_IDENT
                and tokens[i + 1].value in _TYPED_ARRAY_KINDS
            ):
                kind_tok = tokens[i + 1]
                result.add(
                    Diagnostic(
                        file,
                        kind_tok.line,
                        kind_tok.col,
                        kind_tok.end_line,
                        kind_tok.end_col,
                        "typed_array_syntax",
                        f"typed-array prefix '[{kind_tok.value} ...]' is missing the ';' separator; "
                        f"use '[{kind_tok.value}; ...]'",
                    )
                )
        out.append(t)
        i += 1
    return out


def validate_text(text: str, *, file: str = "<input>") -> ValidationResult:
    """Validate an SNBT string. Returns a ``ValidationResult``."""
    result = ValidationResult()
    try:
        raw_tokens = list(_iter_tokens(text))
    except LexError as e:
        result.add(
            Diagnostic(
                file,
                e.line,
                e.col,
                e.line,
                e.col,
                "lex_error",
                e.message,
            )
        )
        return result
    tokens = _strip_typed_array_prefix(raw_tokens, result, file)
    # Make sure the EOF sentinel isn't preceded by a stray comma/colon
    # without a following value.
    parser = _Parser(tokens, result, file)
    parser.parse_top()
    return result


def validate_file(path: str | os.PathLike[str]) -> ValidationResult:
    """Validate a single SNBT file by path."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # SNBT is plain ASCII (extended with the ∞ character). If a file
        # isn't UTF-8 decodable, surface that clearly rather than silently
        # reading it with the wrong codec.
        result = ValidationResult()
        result.add(
            Diagnostic(
                str(p),
                1,
                1,
                1,
                1,
                "encoding_error",
                "file is not valid UTF-8; SNBT must be UTF-8 encoded",
            )
        )
        return result
    except OSError as e:
        result = ValidationResult()
        result.add(
            Diagnostic(
                str(p),
                1,
                1,
                1,
                1,
                "io_error",
                f"could not read file: {e}",
            )
        )
        return result
    return validate_text(text, file=str(p))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _iter_target_files(targets: list[str]) -> Iterator[Path]:
    """Yield every .snbt file under each target. Targets can be files or
    directories; symlinks are followed."""
    for raw in targets:
        p = Path(raw)
        if p.is_file():
            yield p
            continue
        if p.is_dir():
            # Recurse but skip anything that looks like a VCS / build dir.
            for sub in p.rglob("*.snbt"):
                # Skip obvious non-source directories.
                if any(part in sub.parts for part in (".git", "node_modules", "build", "dist", ".gradle")):
                    continue
                yield sub
            continue
        # Neither file nor dir. Defer the error to the caller.
        yield p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate FTB SNBT files (https://docs.feed-the-beast.com/mod-docs/mods/technical/SNBT/).",
    )
    ap.add_argument(
        "targets",
        nargs="+",
        help="one or more .snbt files or directories to scan",
    )
    ap.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    ap.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colors in text output",
    )
    args = ap.parse_args(argv)

    results: list[tuple[Path, ValidationResult]] = []
    seen_paths: set[Path] = set()
    invocation_error = False
    for t in args.targets:
        p = Path(t)
        if not p.exists():
            print(f"error: {t}: no such file or directory", file=sys.stderr)
            invocation_error = True
            continue
        for f in _iter_target_files([t]):
            if f in seen_paths:
                continue
            seen_paths.add(f)
            if f.is_file():
                results.append((f, validate_file(f)))
            else:
                invocation_error = True
                print(
                    f"error: {f}: not a file and not a directory",
                    file=sys.stderr,
                )

    if invocation_error and not results:
        return 2

    if args.format == "json":
        payload = {
            "files": [
                {
                    "path": str(p),
                    "ok": r.ok,
                    "diagnostics": [
                        {
                            "line": d.line,
                            "col": d.col,
                            "end_line": d.end_line,
                            "end_col": d.end_col,
                            "code": d.code,
                            "message": d.message,
                        }
                        for d in r.diagnostics
                    ],
                }
                for p, r in results
            ]
        }
        print(json.dumps(payload, indent=2))
    else:
        for p, r in results:
            for d in r.diagnostics:
                print(d.format(use_color=not args.no_color), file=sys.stderr)
        if any(r.ok for _, r in results):
            ok_count = sum(1 for _, r in results if r.ok)
            err_count = len(results) - ok_count
            print(
                f"\nValidated {len(results)} file(s): {ok_count} OK, {err_count} with errors",
                file=sys.stderr,
            )

    # Exit 1 if any file had diagnostics.
    return 0 if all(r.ok for _, r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())