import ast
from typing import Optional

import pytest

from flake8_assign_and_return import (
    B781,
    ErrorLoc,
    is_assign_and_return,
    AssignAndReturnVisitor,
    AssignAndReturnCheck,
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

    visitor = AssignAndReturnVisitor()
    visitor.visit(node)
    assert visitor.errors == expected_errors, reason

    assert list(AssignAndReturnCheck(node).run()) == expected_errors, reason
