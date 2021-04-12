import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor
from flake8_pie.utils import is_if_test_func_call


class Visitor(Flake8PieVisitor):
    def visit_If(self, node: ast.If) -> None:
        if is_if_test_func_call(node=node, func_name="bool"):
            self.errors.append(
                PIE788(lineno=node.test.lineno, col_offset=node.test.col_offset)
            )

        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        if is_if_test_func_call(node=node, func_name="bool"):
            self.errors.append(
                PIE788(lineno=node.test.lineno, col_offset=node.test.col_offset)
            )

        self.generic_visit(node)


class Flake8PieCheck788(Flake8PieCheck):
    visitor = Visitor


PIE788 = partial(
    ErrorLoc,
    message="PIE788: no-bool-condition: Remove unnecessary bool() call.",
    type=Flake8PieCheck788,
)
