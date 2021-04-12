from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie781_assign_and_return import PIE781
from flake8_pie.tests.utils import to_errors

func_test_cases = [
    (
        """
def foo():
   x = 'bar'
   return x
""",
        PIE781(lineno=4, col_offset=3),
        "single assign then return of that variable is not allowed",
    ),
    (
        """
def foo():
   x, _ = bar()
   return x
""",
        None,
        "tuple assignment then return is allowed",
    ),
    (
        """
def foo():
   bar()
   return x
""",
        None,
        "function call, not assign, and just a return of something",
    ),
    (
        """
def foo():
   pass
""",
        None,
        "empty function can't assign and return",
    ),
    (
        """
def foo():
   x = "foo"
   return 1
""",
        None,
        "valid because we don't return the useless assignment",
    ),
    (
        """
def foo():
   z = "foo"
   return x
""",
        None,
        "valid as don't return the useless assignment, but we don't warn "
        "about the useless assignment since that is already handled by flake8",
    ),
    (
        """
def get_foo(id) -> Optional[Foo]:
    maybeFoo: Optional[Foo] = Foo.objects.filter(
        id=id
    ).first()
    return maybeFoo
""",
        PIE781(lineno=6, col_offset=4),
        "even though we are assigning with a type, a cast would be better "
        "and would remove the extra assignment",
    ),
    (
        """
def get_foo(id) -> Optional[Foo]:
    maybeFoo: Optional[Foo] = Foo.objects.filter(
        id=id
    ).first()
    return bar
""",
        None,
        "we return a different variable",
    ),
]


@pytest.mark.parametrize("func,expected,reason", func_test_cases)
def test_is_assign_and_return(func: str, expected: Error | None, reason: str) -> None:
    expected_errors = [expected] if expected is not None else []
    assert (
        to_errors(Flake8PieCheck(ast.parse(func), filename="foo.py").run())
    ) == expected_errors, reason
