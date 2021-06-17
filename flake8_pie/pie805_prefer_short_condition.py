from __future__ import annotations

import ast

from flake8_pie.base import Error


def trees_equal(left: ast.expr, right: ast.expr) -> bool:
    # TODO: :D
    ...


def pie805_prefer_short_condition(node: ast.IfExp, errors: list[Error]) -> None:
    node.test, node.body
    if trees_equal(node.test, node.body):
        errors.append(PIE805(lineno=node.lineno, col_offset=node.col_offset))


def PIE805(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE805: prefer-short-condition: User 'or' instead of the if expression.",
    )
