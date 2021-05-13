from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie804_no_unnecessary_dict_kwargs import PIE804
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
foo(**{"bar": True})
""",
        errors=[PIE804(lineno=2, col_offset=6)],
    ),
    ex(
        code="""
foo(**{"r2d2": True})
""",
        errors=[PIE804(lineno=2, col_offset=6)],
    ),
    ex(
        code="""
Foo.objects.create(**{"bar": True})
""",
        errors=[PIE804(lineno=2, col_offset=21)],
    ),
    ex(
        code="""
Foo.objects.create(**{"_id": some_id})
""",
        errors=[PIE804(lineno=2, col_offset=21)],
    ),
    ex(
        code="""
foo(**buzz)
foo(**{"bar-foo": True})
foo(**{"bar foo": True})
foo(**{"1foo": True})
foo(**{buzz: True})
foo(**{"": True})
foo(**{f"buzz__{bar}": True})
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
