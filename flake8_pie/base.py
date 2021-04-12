from __future__ import annotations

from typing import NamedTuple


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
