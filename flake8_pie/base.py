from __future__ import annotations

import ast
from typing import NamedTuple

from typing_extensions import Protocol


class Body(Protocol):
    @property
    def body(self) -> list[ast.stmt]:
        ...


class Flake8Error(NamedTuple):
    """
    location of the lint infraction

    Required format for flake8 errors.
    """

    lineno: int
    col_offset: int

    message: str
    type: object


class Error(NamedTuple):
    lineno: int
    col_offset: int
    message: str
