from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


class Visitor(Flake8PieVisitor):
    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Compare):
            self.errors.append(PIE791(lineno=node.lineno, col_offset=node.col_offset))

        self.generic_visit(node)


class Flake8PieCheck791(Flake8PieCheck):
    visitor = Visitor


PIE791 = partial(
    ErrorLoc,
    message="PIE791: no-pointless-statements: Statement looks unnecessary.",
    type=Flake8PieCheck791,
)
