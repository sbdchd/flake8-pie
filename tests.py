import ast
from typing import Optional

import pytest

from flake8_pie import (
    B781,
    ErrorLoc,
    is_assign_and_return,
    Flake8PieVisitor,
    Flake8PieCheck,
)


func_test_cases = [
    (
        """
def foo():
   x = 'bar'
   return x
""",
        B781(lineno=4, col_offset=3),
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
        B781(lineno=6, col_offset=4),
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
def test_is_assign_and_return(
    func: str, expected: Optional[ErrorLoc], reason: str
) -> None:

    node = ast.parse(func)

    func_def = node.body[0]
    assert isinstance(func_def, ast.FunctionDef)
    assert is_assign_and_return(func_def) == expected, reason

    expected_errors = [expected] if expected is not None else []

    visitor = Flake8PieVisitor()
    visitor.visit(node)
    assert visitor.errors == expected_errors, reason

    assert list(Flake8PieCheck(node).run()) == expected_errors, reason
