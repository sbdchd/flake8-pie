from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie805_prefer_literal import PIE805
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
"foo".encode()
""",
        errors=[PIE805(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
"foo".encode("utf-8")
""",
        errors=[PIE805(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
"foo".encode("utf8")
""",
        errors=[PIE805(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
b"foo"
"foo".encode("ascii")
"foo".encode("bar")
"😀".encode()
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
