from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck792
from flake8_pie.pie792_no_inherit_object import PIE792
from flake8_pie.tests.utils import ErrorLoc, ex


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code="""
class Foo(object):
    pass
""",
            errors=[PIE792(lineno=2, col_offset=10)],
        ),
        ex(
            code="""
class object:
    pass

class Foo(object):
    pass
""",
            errors=[PIE792(lineno=5, col_offset=10)],
        ),
        ex(
            code="""
class Foo(Bar, object):
    pass
""",
            errors=[PIE792(lineno=2, col_offset=15)],
        ),
        ex(
            code="""
class Foo(Bar):
    pass
""",
            errors=[],
        ),
        ex(
            code="""
class Foo:
    pass
""",
            errors=[],
        ),
    ],
)
def test_no_inherit_object(code: str, errors: list[ErrorLoc]) -> None:
    expr = ast.parse(code)
    assert list(Flake8PieCheck792(expr, filename="foo.py").run()) == errors
