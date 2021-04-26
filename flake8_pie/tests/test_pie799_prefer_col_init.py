from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie799_prefer_col_init import PIE799
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
bar = []
foo = Foo()
bar.append(foo)
""",
        errors=[PIE799(lineno=4, col_offset=0)],
    ),
    ex(
        code="""
bar = []
bar.append(Foo())
""",
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
def fn() -> list[Foo]:
    foos = []
    foo = Foo()
    foos.append(foo)
    return foos
""",
        errors=[PIE799(lineno=5, col_offset=4)],
    ),
    ex(
        code="""
bar: list[int] = []
bar.append(Foo())
""",
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
bar = []
bar.append(Foo())
bar.append(Foo())
""",
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
bar = []
x: int = 10
x += buzz
bar.append(x)
""",
        errors=[PIE799(lineno=5, col_offset=0)],
    ),
    ex(
        # for loop allows the append() later on
        code="""
bar = []
for el in range(buzz):
    if el.fuzz > 10:
        bar.append("foo")
    else:
        bar.append("foo")
foo = "foo bar buzz"
bar.append(foo)
""",
        errors=[],
    ),
    ex(
        code="""
bar = [Foo()]
bar.append(Foo())
    """,
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
s: Deque[str] = deque()
s.append(Foo())
""",
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
s = deque()
s.appendleft(Foo())
""",
        errors=[PIE799(lineno=3, col_offset=0)],
    ),
    ex(
        code="""
s = deque(bar)
s.append("foo")
""",
        errors=[],
    ),
    ex(
        code="""
foo = Foo()
bar = [foo]
""",
        errors=[],
    ),
    ex(
        code="""
s: Deque[str] = deque(["start"])
s.append("foo")
""",
        errors=[],
    ),
    ex(
        code="""
s = deque(["start"])
s.append("foo")
""",
        errors=[],
    ),
    ex(
        code="""
s = deque(("start",))
s.append("foo")
""",
        errors=[],
    ),
    ex(
        code="""
s = deque(bar)
s.append(Foo())
""",
        errors=[],
    ),
    ex(
        code="""
foos = []
if buzz:
    foos.append(Foo())
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_prefer_literal(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
