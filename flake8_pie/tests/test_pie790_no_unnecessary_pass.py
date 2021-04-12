from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie790_no_unnecessary_pass import PIE790
from flake8_pie.tests.utils import Error, ex, to_errors


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code='''
class Foo:
    """buzz"""
    pass
''',
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code='''
def foo() -> None:
    """
    buzz
    """

    pass
''',
            errors=[PIE790(lineno=7, col_offset=4)],
        ),
        ex(
            code="""
class Foo:
    # bar
    pass
""",
            errors=[],
        ),
        ex(
            code="""
if foo:
    # foo
    pass
""",
            errors=[],
        ),
        ex(
            code="""
class Error(Exception):
    pass
""",
            errors=[],
        ),
        ex(
            code="""
try:
    foo()
except NetworkError:
    pass
""",
            errors=[],
        ),
        ex(
            code="""
def foo() -> None:
    pass
""",
            errors=[],
        ),
    ],
)
def test_no_unnecessary_pass(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
