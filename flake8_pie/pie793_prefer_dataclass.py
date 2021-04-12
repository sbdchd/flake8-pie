from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def _is_suspicious_assignment_stmt(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.AnnAssign)
        and isinstance(stmt.target, ast.Name)
        and stmt.target.id != "__slots__"
    )


def is_prefer_dataclass(
    node: ast.ClassDef, inside_inheriting_cls_stack: list[bool]
) -> Error | None:
    inside_inheriting_cls = (
        inside_inheriting_cls_stack and inside_inheriting_cls_stack[-1]
    )
    if (
        not inside_inheriting_cls
        and not node.bases
        and not node.decorator_list
        and any(_is_suspicious_assignment_stmt(stmt) for stmt in node.body)
    ):
        return PIE793(lineno=node.lineno, col_offset=node.col_offset)
    return None


PIE793 = partial(
    Error, message="PIE793: prefer-dataclass: Consider using a @dataclass."
)
