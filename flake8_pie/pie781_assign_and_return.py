from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def _get_assign_target_id(stmt: ast.stmt) -> str | None:
    """
    We can have two types of assignments statements:
        - ast.Assign: usual assignment
        - ast.AnnAssign: assignment with a type hint

    Here we check accordingly and return the `id`.
    """
    if (
        isinstance(stmt, ast.Assign)
        and len(stmt.targets) == 1
        and isinstance(stmt.targets[0], ast.Name)
    ):
        return stmt.targets[0].id
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
        return stmt.target.id
    return None


def pie781_assign_and_return(func: ast.FunctionDef, errors: list[Error]) -> None:
    """
    check a FunctionDef for assignment and return where a user assigns to a
    variable and returns that variable instead of just returning
    """
    # assign and return can only occur with at least two statements
    if len(func.body) >= 2:
        return_stmt = func.body[-1]
        if isinstance(return_stmt, ast.Return) and isinstance(
            return_stmt.value, ast.Name
        ):
            assign_stmt = func.body[-2]
            assign_id = _get_assign_target_id(assign_stmt)
            if return_stmt.value.id == assign_id:
                errors.append(
                    PIE781(lineno=return_stmt.lineno, col_offset=return_stmt.col_offset)
                )


PIE781 = partial(
    Error,
    message="PIE781: You are assigning to a variable and then returning. Instead remove the assignment and return.",
)
