from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def is_no_unnecessary_pass(node: ast.ClassDef | ast.FunctionDef) -> Error | None:
    if (
        len(node.body) > 1
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Str)
        and isinstance(node.body[1], ast.Pass)
    ):
        return PIE790(lineno=node.body[1].lineno, col_offset=node.body[1].col_offset)

    return None


PIE790 = partial(Error, message="PIE790: no-unnecessary-pass: `pass` can be removed.")
