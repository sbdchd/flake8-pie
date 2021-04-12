from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie788_no_bool_condition import PIE788
from flake8_pie.tests.utils import Error, ex, to_errors


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code="""
if bool(foo): ...
""",
            errors=[PIE788(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
if not bool(foo): ...
""",
            errors=[PIE788(lineno=2, col_offset=3)],
        ),
        ex(
            code="""
x = "foo" if bool(foo) else "bar"
""",
            errors=[PIE788(lineno=2, col_offset=13)],
        ),
        ex(
            code="""
x = "foo" if not bool(foo) else "bar"
""",
            errors=[PIE788(lineno=2, col_offset=13)],
        ),
        ex(
            code="""
if bool(foo) is True: ...
""",
            errors=[],
        ),
        ex(
            code="""
if bool(foo) is False: ...
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
def test_no_bool_condition(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
