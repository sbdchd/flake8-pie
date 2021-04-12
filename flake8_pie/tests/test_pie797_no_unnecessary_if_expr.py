from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie797_no_unnecessary_if_expr import PIE797
from flake8_pie.tests.utils import Error, ex, to_errors

NO_UNNECSSARY_IF_EXPR = [
    ex(
        code="""
foo(is_valid=True if buzz() else False)
""",
        errors=[PIE797(lineno=2, col_offset=13)],
    ),
    ex(
        code="""
foo(is_valid=False if buzz() else True)
""",
        errors=[PIE797(lineno=2, col_offset=13)],
    ),
    ex(
        code="""
bar(is_valid=None if buzz() else True)
""",
        errors=[],
    ),
    ex(
        code="""
bar(is_valid=10 if buzz() else 0)
""",
        errors=[],
    ),
    ex(
        code="""
bar(is_valid=bool(buzz()))
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", NO_UNNECSSARY_IF_EXPR)
def test_no_unnecessary_if_expr(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
