from __future__ import annotations

from typing import NamedTuple

from flake8_pie.base import ErrorLoc


class ex(NamedTuple):
    code: str
    errors: list[ErrorLoc]
