from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie800_no_unnecessary_spread import PIE800
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
foo({**foo, **{"bar": True}})
""",
        errors=[PIE800(lineno=2, col_offset=14)],
    ),
    ex(
        code="""
{**foo, **{bar: 10}}
""",
        errors=[PIE800(lineno=2, col_offset=10)],
    ),
    ex(
        code="""
{**foo, **buzz, **{bar: 10}}
""",
        errors=[PIE800(lineno=2, col_offset=18)],
    ),
    ex(
        code="""
bar = {**foo, "bar": True }
Table.objects.filter(inst=inst, **{f"foo__{bar}__exists": True})
buzz = {**foo, "bar": { 1: 2 }}
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
