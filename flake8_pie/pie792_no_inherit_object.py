from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


class Visitor(Flake8PieVisitor):
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "object":
                self.errors.append(
                    PIE792(lineno=base.lineno, col_offset=base.col_offset)
                )

        self.generic_visit(node)


class Flake8PieCheck792(Flake8PieCheck):
    visitor = Visitor


PIE792 = partial(
    ErrorLoc,
    message="PIE792: no-inherit-object: Inheriting from object is unnecssary in python3.",
    type=Flake8PieCheck792,
)
