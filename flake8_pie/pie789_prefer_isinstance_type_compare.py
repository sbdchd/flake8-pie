import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


class Visitor(Flake8PieVisitor):
    def visit_If(self, node: ast.If) -> None:
        if (
            isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Call)
            and isinstance(node.test.left.func, ast.Name)
            and node.test.left.func.id == "type"
        ):
            self.errors.append(
                PIE789(lineno=node.test.lineno, col_offset=node.test.col_offset)
            )

        self.generic_visit(node)


class Flake8PieCheck789(Flake8PieCheck):
    visitor = Visitor


PIE789 = partial(
    ErrorLoc,
    message="PIE789: prefer-isinstance-type-compare: Use isinstance for comparing types.",
    type=Flake8PieCheck789,
)
