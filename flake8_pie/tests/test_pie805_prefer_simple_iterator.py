from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie805_prefer_simple_iterator import PIE805
from flake8_pie.tests.utils import ex, to_errors

EXAMPLES = [
    ex(
        code="""
for _idx, foo in enumerate(bar):
    ...
""",
        errors=[
            PIE805(lineno=2, col_offset=0, suggestion="use `for foo in enumerate(...)`")
        ],
    ),
    ex(
        code="""
for _key, value in foo.items():
    ...
""",
        errors=[
            PIE805(lineno=2, col_offset=0, suggestion="use `for value in foo.values()`")
        ],
    ),
    ex(
        code="""
for key, _value in foo.items():
    ...
""",
        errors=[
            PIE805(lineno=2, col_offset=0, suggestion="use `for key in foo.keys()`")
        ],
    ),
    ex(
        code="""
fields = [
    k for k, _v in serialize(user).fields.items() if k != "internal"
]
""",
        errors=[PIE805(lineno=3, col_offset=4, suggestion="use `for k in foo.keys()`")],
    ),
    ex(
        code="""
users = (
    User(data)
    for _id, data in user_map.items()
    for f, _y in blah.items()
)
""",
        errors=[
            PIE805(lineno=3, col_offset=4, suggestion="use `for data in foo.values()`"),
            PIE805(lineno=3, col_offset=4, suggestion="use `for f in foo.keys()`"),
        ],
    ),
    # we need to do usage analysis on the variables to determine if they are actually unused instead of looking at `_`.
    ex(
        code="""
[dict(_name=_name, data=data) for _name, data in users.items()]
""",
        errors=[
            PIE805(lineno=2, col_offset=1, suggestion="use `for data in foo.values()`")
        ],
    ),
    ex(
        code="""
for key, value in foo.items():
    ...
for idx, foo in enumerate(bar):
    ...
[k for k, v in users.items() if v == "guest"]
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
