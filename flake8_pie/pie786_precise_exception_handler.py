from typing import Optional
from functools import partial
import ast

from flake8_pie.base import ErrorLoc, Flake8PieVisitor, Flake8PieCheck


class Flake8Pie786Visitor(Flake8PieVisitor):
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        error = is_broad_except(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)


BAD_EXCEPT_IDS = {"BaseException", "Exception"}


def is_bad_except_type(except_type: Optional[ast.Name]) -> bool:
    return except_type is None or except_type.id in BAD_EXCEPT_IDS


def is_broad_except(node: ast.ExceptHandler) -> Optional[ErrorLoc]:
    """
    ensure try...except is not called with Exception, BaseException, or no argument
    """
    if isinstance(node.type, ast.Tuple):
        for elt in node.type.elts:
            if (isinstance(elt, ast.Name) or elt is None) and is_bad_except_type(elt):
                return PIE786(lineno=elt.lineno, col_offset=elt.col_offset)
        return None
    if (isinstance(node.type, ast.Name) or node.type is None) and is_bad_except_type(
        node.type
    ):
        return PIE786(lineno=node.lineno, col_offset=node.col_offset)
    return None


class Flake8PieCheck786(Flake8PieCheck):
    visitor = Flake8Pie786Visitor


PIE786 = partial(
    ErrorLoc, message="PIE786: Use precise exception handlers.", type=Flake8PieCheck786
)
