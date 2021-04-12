from __future__ import annotations

import ast
from functools import partial
from typing import Sequence

from flake8_pie.base import Error


def pie795_prefer_stdlib_enums(
    node: ast.ClassDef, errors: list[Error], inside_inheriting_cls_stack: Sequence[bool]
) -> None:
    inside_inheriting_cls = (
        inside_inheriting_cls_stack and inside_inheriting_cls_stack[-1]
    )
    if (
        not inside_inheriting_cls
        and not node.bases
        and not node.decorator_list
        and len(node.body) > 1
        and all(
            isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.Num, ast.Str))
            for stmt in node.body
        )
    ):
        errors.append(PIE795(lineno=node.lineno, col_offset=node.col_offset))


PIE795 = partial(
    Error,
    message="PIE795: prefer-stdlib-enum: Considering using the builtin enum type.",
)
