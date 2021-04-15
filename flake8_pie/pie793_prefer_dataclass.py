from __future__ import annotations

import ast
from functools import partial
from typing import Sequence

from flake8_pie.base import Error


def _has_dataclass_like_body(body: Sequence[ast.stmt]) -> bool:
    """
    Has at least one dataclass like assignment stmt and doesn't have any
    methods besides __init__.
    """
    found_assignment_stmt = False
    for stmt in body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
            continue
        elif isinstance(stmt, ast.AnnAssign):
            found_assignment_stmt = True
        else:
            return False
    return found_assignment_stmt


def pie793_prefer_dataclass(
    node: ast.ClassDef, errors: list[Error], inside_inheriting_cls_stack: Sequence[bool]
) -> None:
    inside_inheriting_cls = (
        inside_inheriting_cls_stack and inside_inheriting_cls_stack[-1]
    )
    if (
        not inside_inheriting_cls
        and not node.bases
        and not node.decorator_list
        and _has_dataclass_like_body(node.body)
    ):
        errors.append(PIE793(lineno=node.lineno, col_offset=node.col_offset))


PIE793 = partial(
    Error, message="PIE793: prefer-dataclass: Consider using a @dataclass."
)
