from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def is_return_bool(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Return)
        and isinstance(stmt.value, ast.NameConstant)
        and isinstance(stmt.value.value, bool)
    )


def pie802_prefer_simple_return(node: ast.Call, errors: list[Error]) -> None:
    if (
        not isinstance(node.func, ast.Name)
        or node.func.id not in {"all", "any"}
        or len(node.args) != 1
    ):
        return
    argument = node.args[0]
    if isinstance(argument, ast.ListComp):
        errors.append(PIE802(lineno=argument.lineno, col_offset=argument.col_offset))


PIE802 = partial(
    Error, message="PIE802: prefer-simple-any-all: remove unnecessary comprehension."
)
