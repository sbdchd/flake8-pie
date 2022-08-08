from __future__ import annotations

import ast

from flake8_pie.base import Error


def pie807_prefer_list_builtin(node: ast.Lambda, errors: list[Error]) -> None:
    if (
        len(node.args.args) == 0
        and isinstance(node.body, ast.List)
        and len(node.body.elts) == 0
    ):
        errors.append(err(lineno=node.lineno, col_offset=node.col_offset))


def err(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE807 prefer-list-builtin: use the builtin list type instead of a lambda.",
    )
