from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def get_unnecessary_pass_error(node: ast.ClassDef | ast.FunctionDef) -> ErrorLoc | None:
    if (
        len(node.body) > 1
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Str)
        and isinstance(node.body[1], ast.Pass)
    ):
        return PIE790(lineno=node.body[1].lineno, col_offset=node.body[1].col_offset)

    return None


class Visitor(Flake8PieVisitor):
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        error = get_unnecessary_pass_error(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        error = get_unnecessary_pass_error(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)


class Flake8PieCheck790(Flake8PieCheck):
    visitor = Visitor


PIE790 = partial(
    ErrorLoc,
    message="PIE790: no-unnecessary-pass: `pass` can be removed.",
    type=Flake8PieCheck790,
)
