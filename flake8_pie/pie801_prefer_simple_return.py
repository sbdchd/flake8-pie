from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Body, Error


def is_return_bool(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Return)
        and isinstance(stmt.value, ast.NameConstant)
        and isinstance(stmt.value.value, bool)
    )


def pie801_prefer_simple_return(node: Body, errors: list[Error]) -> None:
    for index, stmt in enumerate(node.body):
        if isinstance(stmt, ast.If):
            # we only want "If" statements with a single "Return" of a "bool".
            if len(stmt.body) != 1 or not is_return_bool(stmt.body[0]):
                continue

            if len(stmt.orelse) == 1 and is_return_bool(stmt.orelse[0]):
                errors.append(PIE801(lineno=stmt.lineno, col_offset=stmt.col_offset))
                continue

            # the next statement after the "If" should also return a bool
            try:
                next_stmt = node.body[index + 1]
            except IndexError:
                continue
            if is_return_bool(next_stmt):
                errors.append(PIE801(lineno=stmt.lineno, col_offset=stmt.col_offset))


PIE801 = partial(
    Error,
    message="PIE801: prefer-simple-return: Return your boolean expression directly.",
)
