from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def get_target_node(stmt: ast.stmt) -> ast.Name | None:
    if isinstance(stmt, ast.Assign):
        if len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                return target
    elif isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name):
            return stmt.target
    return None


class Visitor(Flake8PieVisitor):
    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        self.inside_inheriting_cls_stack: list[bool] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        inside_inheriting_cls = (
            self.inside_inheriting_cls_stack and self.inside_inheriting_cls_stack[-1]
        )
        if (
            not inside_inheriting_cls
            and not node.bases
            and not node.decorator_list
            and len(node.body) > 1
            and all(
                isinstance(stmt, ast.Assign)
                and isinstance(stmt.value, (ast.Num, ast.Str))
                for stmt in node.body
            )
        ):
            self.errors.append(PIE795(lineno=node.lineno, col_offset=node.col_offset))

        is_inheriting_cls = len(node.bases) > 0
        self.inside_inheriting_cls_stack.append(is_inheriting_cls)

        self.generic_visit(node)

        self.inside_inheriting_cls_stack.pop()


class Flake8PieCheck795(Flake8PieCheck):
    visitor = Visitor


PIE795 = partial(
    ErrorLoc,
    message="PIE795: prefer-stdlib-enum: Considering using the builtin enum type.",
    type=Flake8PieCheck795,
)
