from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie805_prefer_short_condition import PIE805
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
foo = bar if bar else None
""",
        errors=[PIE805(lineno=2, col_offset=6)],
    ),
    ex(
        code="""
foo = bar.buzz if bar.buzz else None
""",
        errors=[PIE805(lineno=2, col_offset=6)],
    ),
    ex(
        code="""
foo = bar.buzz[0] if bar.buzz[0] else None
""",
        errors=[PIE805(lineno=2, col_offset=6)],
    ),
    ex(
        code="""
# conditionals are allowed
foo = bar if bar is None else None
foo = bar if bar is not None else None
foo = bar if bar > 10 else None
foo = bar if len(bar) > 0 else None
foo = bar if bar() else None

# allow cases where the test doesn't match the body
foo = bar.buzz if bar else None
foo = buzz if bar else None

foo = bar or buzz
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
