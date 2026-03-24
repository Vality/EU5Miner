"""Structural analysis helpers for Clausewitz-style text files."""

from __future__ import annotations

import re
from dataclasses import dataclass

ENTRY_MODE_RE = re.compile(
    r"\b(INJECT|REPLACE|TRY_INJECT|TRY_REPLACE|INJECT_OR_CREATE|REPLACE_OR_CREATE):[A-Za-z0-9_.$-]+"
)
GUI_EXPRESSION_RE = re.compile(r"\[[^\]\n]+\]")
MACRO_RE = re.compile(r"\$[A-Za-z0-9_]+\$")
SCOPED_IDENTIFIER_RE = re.compile(r"\b(?:scope|root|from|prev|actor|recipient):[A-Za-z0-9_().]+")
TYPED_REFERENCE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*:[A-Za-z0-9_.]+")


@dataclass(frozen=True)
class ScriptFeatures:
    balanced_braces: bool
    brace_depth: int
    comment_lines: int
    gui_expression_count: int
    macro_count: int
    scoped_reference_count: int
    typed_reference_count: int
    entry_mode_count: int


def analyze_script_text(text: str) -> ScriptFeatures:
    """Analyze broad structural features without building a full parser."""

    brace_depth = 0
    balanced_braces = True
    comment_lines = 0
    in_string = False
    escaped = False

    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            comment_lines += 1

        index = 0
        while index < len(line):
            char = line[index]

            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                index += 1
                continue

            if char == "#":
                break
            if char == '"':
                in_string = True
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth < 0:
                    balanced_braces = False
                    brace_depth = 0
            index += 1

    if in_string or brace_depth != 0:
        balanced_braces = False

    return ScriptFeatures(
        balanced_braces=balanced_braces,
        brace_depth=brace_depth,
        comment_lines=comment_lines,
        gui_expression_count=len(GUI_EXPRESSION_RE.findall(text)),
        macro_count=len(MACRO_RE.findall(text)),
        scoped_reference_count=len(SCOPED_IDENTIFIER_RE.findall(text)),
        typed_reference_count=len(TYPED_REFERENCE_RE.findall(text)),
        entry_mode_count=len(ENTRY_MODE_RE.findall(text)),
    )
