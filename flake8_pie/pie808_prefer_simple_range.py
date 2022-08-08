from __future__ import annotations

import ast

from flake8_pie.base import Error


def pie808_prefer_simple_range(node: ast.Call, errors: list[Error]) -> None:
    if (
        isinstance(node.func, ast.Name)
        and node.func.id == "range"
        and len(node.args) == 2
        and isinstance(node.args[0], ast.Num)
        and node.args[0].n == 0
    ):
        errors.append(
            err(lineno=node.args[0].lineno, col_offset=node.args[0].col_offset)
        )


def err(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE808 prefer-simple-range: range starts at 0 by default.",
    )
