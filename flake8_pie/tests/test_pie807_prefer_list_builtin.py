from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie807_pefer_list_builtin import err
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
@dataclass
class Foo:
    foo: List[str] = field(default_factory=lambda: [])
""",
        errors=[err(lineno=4, col_offset=43)],
    ),
    ex(
        code="""
class FooTable(BaseTable):
    bar = fields.ListField(default=lambda: [])
""",
        errors=[err(lineno=3, col_offset=35)],
    ),
    ex(
        code="""
class FooTable(BaseTable):
    bar = fields.ListField(lambda: [])
""",
        errors=[err(lineno=3, col_offset=27)],
    ),
    ex(
        code="""
@dataclass
class Foo:
    foo: List[str] = field(default_factory=list)

class FooTable(BaseTable):
    bar = fields.ListField(list)
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
