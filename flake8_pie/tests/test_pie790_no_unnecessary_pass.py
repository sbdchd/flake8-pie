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
            code="""
if foo:
    '''foo'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code="""
if foo:
    pass
else:
    '''bar'''
    pass
""",
            errors=[PIE790(lineno=6, col_offset=4)],
        ),
        ex(
            code="""
while True:
    pass
else:
    '''bar'''
    pass
""",
            errors=[PIE790(lineno=6, col_offset=4)],
        ),
        ex(
            code="""
for _ in range(10):
    pass
else:
    '''bar'''
    pass
""",
            errors=[PIE790(lineno=6, col_offset=4)],
        ),
        ex(
            code="""
async for _ in range(10):
    pass
else:
    '''bar'''
    pass
""",
            errors=[PIE790(lineno=6, col_offset=4)],
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
            code='''
async def foo():
    """
    buzz
    """

    pass
''',
            errors=[PIE790(lineno=7, col_offset=4)],
        ),
        ex(
            code='''
try:
    """
    buzz
    """
    pass
except ValueError:
    pass
''',
            errors=[PIE790(lineno=6, col_offset=4)],
        ),
        ex(
            code="""
try:
    bar()
except ValueError:
    '''bar'''
    pass
""",
            errors=[PIE790(lineno=6, col_offset=4)],
        ),
        ex(
            code="""
for _ in range(10):
    '''buzz'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code="""
async for _ in range(10):
    '''buzz'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code="""
while cond:
    '''buzz'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code="""
with bar:
    '''buzz'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
        ),
        ex(
            code="""
async with bar:
    '''buzz'''
    pass
""",
            errors=[PIE790(lineno=4, col_offset=4)],
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
