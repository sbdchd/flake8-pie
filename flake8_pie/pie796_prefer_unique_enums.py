from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def _extends_enum(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Enum":
            return True
        elif (
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "enum"
            and base.attr == "Enum"
        ):
            return True
    return False


class Visitor(Flake8PieVisitor):
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if _extends_enum(node) and not node.decorator_list:
            self.errors.append(PIE796(lineno=node.lineno, col_offset=node.col_offset))
        self.generic_visit(node)


class Flake8PieCheck796(Flake8PieCheck):
    visitor = Visitor


PIE796 = partial(
    ErrorLoc,
    message="PIE796: prefer-unique-enums: Consider using the @enum.unique decorator.",
    type=Flake8PieCheck796,
)
