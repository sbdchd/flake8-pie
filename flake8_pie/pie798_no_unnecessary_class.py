from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error

ALLOW_DECORATORS = {"staticmethod", "classmethod"}


def _is_possible_instance_method(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if func.args.args and func.args.args[0].arg == "self":
        return True

    if func.decorator_list and any(
        not isinstance(dec, ast.Name) or dec.id not in ALLOW_DECORATORS
        for dec in func.decorator_list
    ):
        return True

    return False


def pie798_no_unnecessary_class(node: ast.ClassDef, errors: list[Error]) -> None:
    if node.bases:
        return
    if not node.body:
        return

    has_func_defined = False
    for stmt in node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_func_defined = True
            if _is_possible_instance_method(stmt):
                return
        elif isinstance(stmt, (ast.AnnAssign, ast.Assign)):
            return

    if has_func_defined:
        errors.append(PIE798(lineno=node.lineno, col_offset=node.col_offset))


PIE798 = partial(
    Error,
    message="PIE798: no-unnecessary-class: Consider using a module for namespacing instead.",
)
