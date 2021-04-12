from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie796_prefer_unique_enums import PIE796
from flake8_pie.tests.utils import ex, to_errors

PREFER_UNIQUE_ENUM_EXAMPLES = [
    ex(
        code="""
class FakeEnum(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[PIE796(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
class FakeEnum(Enum):
    A = 1
    B = 2
    C = 3
""",
        errors=[PIE796(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
class FakeEnum(str, Enum):
    A = 1
    B = 2
    C = 3
""",
        errors=[PIE796(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
@enum.unique
class FakeEnum(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
    ex(
        code="""
@unique
class FakeEnum(Enum):
    A = 1
    B = 2
    C = 3
""",
        errors=[],
    ),
    ex(
        code="""
@my_unique_decorator
class FakeEnum(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
    ex(
        code="""
@foo_decorator
class FakeEnum(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", PREFER_UNIQUE_ENUM_EXAMPLES)
def test_prefer_unique_enums(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
