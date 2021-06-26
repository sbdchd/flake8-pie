from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie806_no_assert_except import PIE806
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
try:
    assert "@" in bar
except AssertionError:
    ...
""",
        errors=[PIE806(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
try:
    assert len(foo) == bar
except AssertionError:
    ...
""",
        errors=[PIE806(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
if len(foo) == bar:
    ...

try:
    foo()
except AssertionError:
    ...

try:
    assert len(foo) == bar
    buzz()
except AssertionError:
    ...

try:
    assert len(foo) == bar
except (AssertionError, SomeOtherError):
    ...
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
