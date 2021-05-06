from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie801_prefer_simple_return import PIE801
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
def main() -> bool:
    if foo > 10:
        return True
    return False
    """,
        errors=[PIE801(lineno=3, col_offset=4)],
    ),
    ex(
        code="""
def main() -> bool:
    if foo > 10:
        return True
    else:
        return False
""",
        errors=[PIE801(lineno=3, col_offset=4)],
    ),
    ex(
        code="""
def main() -> bool:
    return foo > 10
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_prefer_simple_return(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
