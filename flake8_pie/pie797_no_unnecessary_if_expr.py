from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def _is_bool_literal(stmt: ast.expr) -> bool:
    return isinstance(stmt, ast.NameConstant) and (
        stmt.value is True or stmt.value is False
    )


def pie797_no_unnecessary_if_expr(node: ast.IfExp, errors: list[Error]) -> None:
    if _is_bool_literal(node.body) and _is_bool_literal(node.orelse):
        errors.append(PIE797(lineno=node.lineno, col_offset=node.col_offset))


PIE797 = partial(
    Error,
    message="PIE797: no-unnecessary-if-expr: Consider using bool() instead of an if expression.",
)
