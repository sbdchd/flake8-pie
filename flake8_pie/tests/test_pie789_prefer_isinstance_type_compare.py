from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie789_prefer_isinstance_type_compare import PIE789
from flake8_pie.tests.utils import Error, ex, to_errors


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code="""
if type(foo) == str: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if type(foo) is bool: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if type(foo) is not dict: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if type(foo) == Bar: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
foo = "bar" if type(foo) == Bar else "buzz"
""",
            errors=[PIE789(lineno=2, col_offset=15)],
        ),
        ex(
            code="""
if type(foo) != Bar: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if type(foo) in [int, str]: ...
""",
            errors=[PIE789(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if type(foo): ...
""",
            errors=[],
        ),
        ex(
            code="""
if isinstance(foo, Bar): ...
""",
            errors=[],
        ),
        ex(
            code="""
if not isinstance(foo, Bar): ...
""",
            errors=[],
        ),
    ],
)
def test_prefer_isinstance_type_compare(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
