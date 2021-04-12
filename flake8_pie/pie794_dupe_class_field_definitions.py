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
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        seen_targets: set[str] = set()
        if node.bases and node.body:
            for stmt in node.body:
                target_node = get_target_node(stmt)
                if target_node is None:
                    continue
                if target_node.id in seen_targets:
                    self.errors.append(
                        PIE794(
                            lineno=target_node.lineno, col_offset=target_node.col_offset
                        )
                    )
                else:
                    seen_targets.add(target_node.id)

        self.generic_visit(node)


class Flake8PieCheck794(Flake8PieCheck):
    visitor = Visitor


PIE794 = partial(
    ErrorLoc,
    message="PIE794: no-dupe-class-field-defs: This field is duplicated.",
    type=Flake8PieCheck794,
)
