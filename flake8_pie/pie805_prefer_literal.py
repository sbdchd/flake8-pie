from __future__ import annotations

import ast

from flake8_pie.base import Error

UTF8_ENCODE_NAMES = frozenset({"utf8", "utf-8"})


def pie805_prefer_literal(node: ast.Call, errors: list[Error]) -> None:
    if (
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Str)
        and node.func.attr == "encode"
        and (
            len(node.args) == 0
            or (
                len(node.args) == 1
                and isinstance(node.args[0], ast.Str)
                and node.args[0].s in UTF8_ENCODE_NAMES
            )
        )
        and node.func.value.s.isascii()
    ):
        literal_str_node = node.func.value
        errors.append(
            PIE805(
                lineno=literal_str_node.lineno, col_offset=literal_str_node.col_offset
            )
        )


def PIE805(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE805 prefer-literal: Prefer the byte string literal rather than calling encode.",
    )
