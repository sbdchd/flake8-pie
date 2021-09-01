from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie809_django_prefer_bulk import err
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
[Item.objects.create(item) for item in items]
""",
        errors=[err(lineno=2, col_offset=1)],
    ),
    ex(
        code="""
[Item.objects.create(item) for item in [bar for bar in buzz]]
""",
        errors=[err(lineno=2, col_offset=1)],
    ),
    ex(
        code="""
(Item.objects.create(item) for item in items)
""",
        errors=[err(lineno=2, col_offset=1)],
    ),
    ex(
        code="""
Item.objects.insert(items)
Item.objects.create(item)
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
