from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie802_prefer_simple_any_all import PIE802
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
all((x.id for x in bar))
all(x.id for x in bar)
    """,
        # parentheses aren't in the AST so we cannot reliably differentiate
        # these two.
        errors=[],
    ),
    ex(
        code="""
any([x.id for x in bar])
""",
        errors=[PIE802(lineno=2, col_offset=5)],
    ),
    ex(
        code="""
all([x.id for x in bar])
""",
        errors=[PIE802(lineno=2, col_offset=5)],
    ),
    ex(
        code="""
all(x.id for x in bar)
any(x.id for x in bar)
any({x.id for x in bar})
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_prefer_simple_any_all(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
