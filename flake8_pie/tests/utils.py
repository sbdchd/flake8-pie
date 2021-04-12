from __future__ import annotations

from typing import Iterable, NamedTuple

from flake8_pie.base import Error, Flake8Error


class ex(NamedTuple):
    code: str
    errors: list[Error]


def to_errors(flake8_err: Iterable[Flake8Error]) -> list[Error]:
    return [
        Error(lineno=err.lineno, col_offset=err.col_offset, message=err.message)
        for err in flake8_err
    ]
