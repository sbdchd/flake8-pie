from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def is_no_pointless_statements(node: ast.Expr) -> Error | None:
    if isinstance(node.value, ast.Compare):
        return PIE791(lineno=node.lineno, col_offset=node.col_offset)
    return None


PIE791 = partial(
    Error, message="PIE791: no-pointless-statements: Statement looks unnecessary."
)
