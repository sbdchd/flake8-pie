from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def pie789_prefer_isinstance_type_compare(
    node: ast.If | ast.IfExp, errors: list[Error]
) -> None:
    if (
        isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Call)
        and isinstance(node.test.left.func, ast.Name)
        and node.test.left.func.id == "type"
    ):
        errors.append(PIE789(lineno=node.test.lineno, col_offset=node.test.col_offset))


PIE789 = partial(
    Error,
    message="PIE789: prefer-isinstance-type-compare: Use isinstance for comparing types.",
)
