from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def _is_bool_literal(stmt: ast.expr) -> bool:
    return isinstance(stmt, ast.NameConstant) and (
        stmt.value is True or stmt.value is False
    )


class Visitor(Flake8PieVisitor):
    def visit_IfExp(self, node: ast.IfExp) -> None:
        if _is_bool_literal(node.body) and _is_bool_literal(node.orelse):
            self.errors.append(PIE797(lineno=node.lineno, col_offset=node.col_offset))
        self.generic_visit(node)


class Flake8PieCheck797(Flake8PieCheck):
    visitor = Visitor


PIE797 = partial(
    ErrorLoc,
    message="PIE797: no-unnecessary-if-expr: Consider using bool() instead of an if expression.",
    type=Flake8PieCheck797,
)
