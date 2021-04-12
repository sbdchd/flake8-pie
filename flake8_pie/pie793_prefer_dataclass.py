from __future__ import annotations

import ast
from functools import partial
from typing import Sequence

from flake8_pie.base import Error


def _is_suspicious_assignment_stmt(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.AnnAssign)
        and isinstance(stmt.target, ast.Name)
        and stmt.target.id != "__slots__"
    )


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
        and any(_is_suspicious_assignment_stmt(stmt) for stmt in node.body)
    ):
        errors.append(PIE793(lineno=node.lineno, col_offset=node.col_offset))


PIE793 = partial(
    Error, message="PIE793: prefer-dataclass: Consider using a @dataclass."
)
