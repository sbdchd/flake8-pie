from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def _is_suspicious_assignment_stmt(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.AnnAssign)
        and isinstance(stmt.target, ast.Name)
        and stmt.target.id != "__slots__"
    )


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
            and any(_is_suspicious_assignment_stmt(stmt) for stmt in node.body)
        ):
            self.errors.append(PIE793(lineno=node.lineno, col_offset=node.col_offset))

        is_inheriting_cls = len(node.bases) > 0
        self.inside_inheriting_cls_stack.append(is_inheriting_cls)

        self.generic_visit(node)

        self.inside_inheriting_cls_stack.pop()


class Flake8PieCheck793(Flake8PieCheck):
    visitor = Visitor


PIE793 = partial(
    ErrorLoc,
    message="PIE793: prefer-dataclass: Consider using a @dataclass.",
    type=Flake8PieCheck793,
)
