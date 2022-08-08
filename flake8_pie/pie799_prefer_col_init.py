from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import partial

from typing_extensions import Literal

from flake8_pie.base import Body, Error


@dataclass(frozen=True)
class ColDecl:
    lineno: int
    name: str
    kind: Literal["list", "deque"]


def _get_assign_target(node: ast.stmt) -> ast.Name | None:
    if (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    ):
        return node.targets[0]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target
    return None


def pie799_prefer_col_init(node: Body, errors: list[Error]) -> None:
    cur_var_name: ColDecl | None = None
    for stmt in node.body:
        # bail out early in case we have control flow, like a for loop that
        # might mutate the variable deceleration.
        if not isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr)):
            cur_var_name = None
            continue

        assign_target = _get_assign_target(stmt)
        if assign_target is not None:
            if isinstance(stmt.value, ast.List):
                cur_var_name = ColDecl(
                    name=assign_target.id, lineno=assign_target.lineno, kind="list"
                )
            if (
                isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and stmt.value.func.id == "deque"
                and len(stmt.value.args) == 0
            ):
                cur_var_name = ColDecl(
                    name=assign_target.id, lineno=assign_target.lineno, kind="deque"
                )

        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and isinstance(stmt.value.func.value, ast.Name)
            and cur_var_name is not None
            and stmt.value.func.value.id == cur_var_name.name
            and (
                (cur_var_name.kind == "list" and stmt.value.func.attr == "append")
                or (
                    cur_var_name.kind == "deque"
                    and stmt.value.func.attr in {"append", "appendleft"}
                )
            )
        ):
            errors.append(PIE799(lineno=stmt.lineno, col_offset=stmt.col_offset))
            cur_var_name = None


PIE799 = partial(
    Error,
    message="PIE799 prefer-col-init: Consider passing values in when creating the collection.",
)
