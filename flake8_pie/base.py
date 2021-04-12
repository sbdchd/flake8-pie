from __future__ import annotations

import ast
from typing import Iterable, NamedTuple


class ErrorLoc(NamedTuple):
    """
    location of the lint infraction

    Required format for flake8 errors.
    """

    lineno: int
    col_offset: int

    message: str
    type: object


class Flake8PieVisitor(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.errors: list[ErrorLoc] = []
        self.filename = filename

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: errors={self.errors}>"


class Flake8PieCheck:
    name = "flake8-pie"
    version = "0.6.1"

    visitor: type[Flake8PieVisitor]

    def __init__(
        self, tree: ast.Module, filename: str, *args: object, **kwargs: object
    ) -> None:
        self.filename = filename
        self.tree = tree

    def run(self) -> Iterable[ErrorLoc]:
        # When using flake8-pyi, skip the stub files.
        if self.filename.endswith(".pyi"):
            return
        visitor = self.visitor(self.filename)

        visitor.visit(self.tree)

        yield from visitor.errors
