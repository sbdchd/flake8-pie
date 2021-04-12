from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie787_no_len_condition import PIE787
from flake8_pie.tests.utils import ex, to_errors


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code="""
if len(foo): ...
""",
            errors=[PIE787(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if not len(foo): ...
""",
            errors=[PIE787(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
x = "foo" if len(foo) else "bar"
""",
            errors=[PIE787(lineno=2, col_offset=13)],
        ),
        ex(
            code="""
x = "buzz" if not len(foo) else "boo"
""",
            errors=[PIE787(lineno=2, col_offset=14)],
        ),
        ex(
            code="""
if len(foo) > 0: ...
""",
            errors=[],
        ),
        ex(
            code="""
if len(foo) == 0: ...
""",
            errors=[],
        ),
        ex(
            code="""
if foo: ...
""",
            errors=[],
        ),
        ex(
            code="""
if not foo: ...
""",
            errors=[],
        ),
    ],
)
def test_no_len_condition(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
