from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck794
from flake8_pie.pie794_dupe_class_field_definitions import PIE794
from flake8_pie.tests.utils import ErrorLoc, ex

NO_DUPE_FIELD_EXAMPLES = [
    ex(
        code="""
class Foo(BaseModel):
    name = StringField()
    # ....
    name = StringField()
    def remove(self) -> None: ...
""",
        errors=[PIE794(lineno=5, col_offset=4)],
    ),
    ex(
        code="""
class Foo(BaseModel):
    name: str = StringField()
    # ....
    name = StringField()
    def foo(self) -> None: ...
""",
        errors=[PIE794(lineno=5, col_offset=4)],
    ),
    ex(
        code="""
class User(BaseModel):
    bar: str = StringField()
    foo: bool = BooleanField()
    # ...
    bar = StringField()
""",
        errors=[PIE794(lineno=6, col_offset=4)],
    ),
    ex(
        code="""
class User(BaseModel):
    @property
    def buzz(self) -> str: ...
    @buzz.setter
    def buzz(self, value: str | int) -> None: ...
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", NO_DUPE_FIELD_EXAMPLES)
def test_no_dupe_class_fields(code: str, errors: list[ErrorLoc]) -> None:
    expr = ast.parse(code)
    assert list(Flake8PieCheck794(expr, filename="foo.py").run()) == errors
