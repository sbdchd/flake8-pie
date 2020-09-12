from typing import NamedTuple, Iterable, List, Type

import ast


class ErrorLoc(NamedTuple):
    """
    location of the lint infraction

    Required format for flake8 errors.
    """

    lineno: int
    col_offset: int

    message: str
    type: "object"


class Flake8PieVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[ErrorLoc] = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: errors={self.errors}>"


class Flake8PieCheck:
    name = "flake8-pie"
    version = "0.6.1"

    visitor: Type["Flake8PieVisitor"]

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree

    def run(self) -> Iterable[ErrorLoc]:
        visitor = self.visitor()

        visitor.visit(self.tree)

        yield from visitor.errors
