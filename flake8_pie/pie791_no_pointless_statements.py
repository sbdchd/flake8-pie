from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def pie791_no_pointless_statements(node: ast.Expr, errors: list[Error]) -> None:
    if isinstance(node.value, ast.Compare) or (
        isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "super"
    ):
        errors.append(PIE791(lineno=node.lineno, col_offset=node.col_offset))


PIE791 = partial(
    Error, message="PIE791: no-pointless-statements: Statement looks unnecessary."
)
