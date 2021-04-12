from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie795_prefer_stdlib_enums import PIE795
from flake8_pie.tests.utils import ex, to_errors

PREFER_STDLIB_ENUM_EXAMPLES = [
    ex(
        code="""
class FakeEnum:
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[PIE795(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
class FakeEnum:
    A = 1
    B = 2
    C = 3
""",
        errors=[PIE795(lineno=2, col_offset=0)],
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
class FakeEnum(Foo):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
    ex(
        code="""
@some_decorator
class FakeEnum:
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
    ex(
        code="""
class Foo:
    foo = "user"
""",
        errors=[],
    ),
    ex(
        code="""
class Foo(Bar):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_name = "user"
""",
        errors=[],
    ),
    ex(
        code="""
class Foo(Bar):

    class Config:
        foo = "user"
        other_foo = "buzz"
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", PREFER_STDLIB_ENUM_EXAMPLES)
def test_prefer_stdlib_enum(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
