"""Self-tests for scripts/validate_snbt.py.

Run with::

    python -m unittest scripts.test_validate_snbt

or::

    python scripts/test_validate_snbt.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make the script importable when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_snbt import validate_text, validate_file  # noqa: E402


def _ok(text: str) -> None:
    """Assert ``text`` validates cleanly with no diagnostics."""
    result = validate_text(text)
    if not result.ok:
        msgs = "\n  ".join(d.format(use_color=False) for d in result.diagnostics)
        raise AssertionError(f"expected valid SNBT, got diagnostics:\n  {msgs}\n--- source ---\n{text}")


def _bad(text: str, code: str | None = None) -> list:
    """Assert ``text`` fails validation. Returns the diagnostics for
    further inspection (e.g. to assert the diagnostic code)."""
    result = validate_text(text)
    if result.ok:
        raise AssertionError(f"expected invalid SNBT, got clean validation:\n--- source ---\n{text}")
    if code is not None:
        codes = [d.code for d in result.diagnostics]
        if code not in codes:
            raise AssertionError(
                f"expected diagnostic code {code!r}, got {codes}\n"
                f"--- source ---\n{text}"
            )
    return result.diagnostics


class ValidSamples(unittest.TestCase):
    """All of these should validate cleanly."""

    def test_empty_object(self) -> None:
        _ok("{}")

    def test_empty_array(self) -> None:
        _ok("[]")

    def test_object_with_comments(self) -> None:
        _ok(
            "# header comment\n"
            "{\n"
            "    # inside comment\n"
            "    key: 1\n"
            "    key2: \"value with #hash\"\n"
            "}\n"
        )

    def test_numbers_with_all_suffixes(self) -> None:
        _ok("{ a: 1 b: 2b c: 3s d: 4l e: 4L f: 1.0f g: 2.0d h: 3.0D i: 1e3 j: 1.5e-2d k: 0xFF }")

    def test_booleans(self) -> None:
        # Same-line multi-element objects require commas per the FTB spec.
        _ok("{ on: true, off: false }")
        # Across newlines, commas are optional.
        _ok(
            "{\n"
            "    on: true\n"
            "    off: false\n"
            "}\n"
        )

    def test_quoted_strings_single_and_double(self) -> None:
        _ok("{ a: \"double\", b: 'single', c: \"with \\n newline\", d: 'with \\t tab' }")

    def test_single_line_object_with_commas(self) -> None:
        _ok("{ a: 1, b: 2, c: 3 }")

    def test_multiline_object_no_commas(self) -> None:
        # Multi-line: commas are OPTIONAL between values per the FTB spec.
        _ok(
            "{\n"
            "    a: 1\n"
            "    b: 2\n"
            "    c: 3\n"
            "}\n"
        )

    def test_multiline_object_mixed_with_and_without_commas(self) -> None:
        # Mixed commas/no-commas is allowed on different lines.
        _ok(
            "{\n"
            "    a: 1,\n"
            "    b: 2\n"
            "    c: 3,\n"
            "}\n"
        )

    def test_numbers_with_all_suffixes(self) -> None:
        _ok("{ a: 1, b: 2b, c: 3s, d: 4l, e: 4L, f: 1.0f, g: 2.0d, h: 3.0D, i: 1e3, j: 1.5e-2d, k: 0xFF }")

    def test_nested_objects(self) -> None:
        _ok(
            "{\n"
            "    outer: {\n"
            "        inner: { flag: true }\n"
            "    }\n"
            "    list: [ 1, 2, 3 ]\n"
            "}\n"
        )

    def test_array_with_infinity_and_nan(self) -> None:
        # Per the FTB spec, same-line multi-element objects require commas.
        _ok("{ a: ∞, b: -∞, c: ∞F, d: -∞F, e: NaN, f: NanF }")

    def test_array_multiline_no_commas(self) -> None:
        # Real FTB config example (wrapped in a top-level object so it
        # parses as a key:value):
        _ok(
            "{ info_hidden: [\n"
            "    \"ftbchunks:fps\"\n"
            "    \"ftbchunks:game_time\"\n"
            "    \"ftbchunks:real_time\"\n"
            "    \"ftbchunks:debug\"\n"
            "] }\n"
        )

    def test_special_identifiers(self) -> None:
        # Keys can be unquoted identifiers; quoted "true"/"false" are strings.
        _ok("{ \"true\": true, \"false\": false, plain: 42 }")

    def test_typed_array_int(self) -> None:
        # Vanilla SNBT typed-array syntax should still validate.
        _ok("{ recents: [I; ] }")
        _ok("{ recents: [I; 1, 2, 3 ] }")

    def test_typed_array_byte(self) -> None:
        _ok("{ data: [B; 0, 1, 2, 127, -128b ] }")

    def test_typed_array_long_class_refs(self) -> None:
        _ok("{ items: [L; \"minecraft:stone\", \"minecraft:dirt\" ] }")

    def test_real_ftbchunks_file(self) -> None:
        """The real ftbchunks-client.snbt should validate cleanly."""
        path = Path(__file__).resolve().parent.parent / "config" / "ftbchunks-client.snbt"
        if not path.exists():
            self.skipTest(f"fixture not present: {path}")
        result = validate_file(path)
        if not result.ok:
            msgs = "\n  ".join(d.format(use_color=False) for d in result.diagnostics)
            self.fail(f"real FTB config file failed validation:\n  {msgs}")

    def test_all_real_snbt_files(self) -> None:
        """Every *.snbt file in the repo should validate cleanly."""
        root = Path(__file__).resolve().parent.parent
        for f in sorted(root.rglob("*.snbt")):
            # Disposable downloads and extracted JAR evidence are not authored
            # pack configuration.  Keep this repository-wide assertion scoped
            # to files that can actually ship.
            if any(part in f.parts for part in (".git", "build", "dist", "tmp")):
                continue
            result = validate_file(f)
            if not result.ok:
                msgs = "\n  ".join(d.format(use_color=False) for d in result.diagnostics)
                self.fail(f"{f} failed validation:\n  {msgs}")


class InvalidSamples(unittest.TestCase):
    """Each of these should produce a diagnostic."""

    def test_unterminated_object(self) -> None:
        _bad("{ a: 1, b: 2", code="unterminated_object")

    def test_unterminated_array(self) -> None:
        _bad("[ 1, 2, 3", code="unterminated_array")

    def test_missing_colon_after_key(self) -> None:
        _bad("{ a 1 }", code="expected_token")

    def test_missing_value_after_colon(self) -> None:
        _bad("{ a: }", code="missing_value")

    def test_stray_closer(self) -> None:
        _bad("}", code="trailing_tokens")

    def test_missing_comma_same_line_array(self) -> None:
        # FTB requires commas between values on the same line.
        _bad("[ 1 2 3 ]", code="missing_comma")

    def test_missing_comma_same_line_object(self) -> None:
        _bad("{ a: 1 b: 2 }", code="missing_comma")

    def test_invalid_number(self) -> None:
        # `1.2.3` cannot be lexed as a number — lexer error.
        _bad("{ a: 1.2.3 }", code="lex_error")

    def test_duplicate_key(self) -> None:
        _bad("{ a: 1, a: 2 }", code="duplicate_key")

    def test_duplicate_key_multiline(self) -> None:
        _bad(
            "{\n"
            "    a: 1\n"
            "    a: 2\n"
            "}\n",
            code="duplicate_key",
        )

    def test_unterminated_string(self) -> None:
        _bad('{ a: "never closes }', code="lex_error")

    def test_unterminated_string_at_eof(self) -> None:
        _bad('{ a: "x', code="lex_error")

    def test_unquoted_value_with_whitespace(self) -> None:
        # Bare identifier as a value is invalid (use quoted string instead).
        _bad("{ a: some unquoted thing }", code="invalid_value")

    def test_typed_array_missing_semicolon(self) -> None:
        _bad("{ data: [B 1, 2 ] }", code="typed_array_syntax")

    def test_typed_array_wrong_element_type(self) -> None:
        # [I; expects numbers, not strings.
        _bad("{ data: [I; \"not a number\" ] }", code="typed_array_element")

    def test_empty_file(self) -> None:
        _bad("", code="empty_file")


if __name__ == "__main__":
    unittest.main()
