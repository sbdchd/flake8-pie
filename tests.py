import ast
from typing import Optional

import pytest

from flake8_pie import (
    PIE781,
    PIE782,
    PIE783,
    ErrorLoc,
    is_assign_and_return,
    Flake8PieCheck,
)


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
def test_is_assign_and_return(
    func: str, expected: Optional[ErrorLoc], reason: str
) -> None:

    node = ast.parse(func)

    func_def = node.body[0]
    assert isinstance(func_def, ast.FunctionDef)
    assert is_assign_and_return(func_def) == expected, reason

    expected_errors = [expected] if expected is not None else []

    assert list(Flake8PieCheck(node).run()) == expected_errors, reason


@pytest.mark.parametrize(
    "func,expected,reason",
    [
        (
            """
x = (
    f"foo {y}",
    f"bar"
)""",
            PIE782(lineno=4, col_offset=4),
            "f string with no templates",
        ),
        ("f'foo {y}'", None, "used template"),
    ],
)
def test_no_pointless_f_strings(
    func: str, expected: Optional[ErrorLoc], reason: str
) -> None:
    node = ast.parse(func)

    expected_errors = [expected] if expected else []
    assert list(Flake8PieCheck(node).run()) == expected_errors, reason


def test_checker_matches_flake8_api() -> None:
    """
    flake8 requires checkers have both a name and a version
    see: https://gitlab.com/pycqa/flake8/blob/027ed1c9cc5087b611630aea08dd67a498e701a4/src/flake8/plugins/manager.py#L110
    """
    assert Flake8PieCheck.version
    assert Flake8PieCheck.name


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            """
@shared_task(bind=True)
def import_users():
    pass
""",
            PIE783(lineno=2, col_offset=1),
        ),
        (
            """
@shared_task(bind=True, name="tasks.import_users")
def import_users():
    pass
""",
            None,
        ),
        (
            """
@app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    serializer="pickle",
)
def send_messages(messages):
    pass
""",
            PIE783(lineno=2, col_offset=1),
        ),
        (
            """
@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_messages(messages):
    pass
""",
            PIE783(lineno=2, col_offset=1),
        ),
        (
            """
@app.task(
    name="emails.tasks.send_messages",
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_messages(messages):
    pass
""",
            None,
        ),
    ],
)
def test_celery_task_name_lint(code: str, expected: Optional[ErrorLoc]) -> None:
    node = ast.parse(code)

    expected_errors = [expected] if expected else []
    assert list(Flake8PieCheck(node).run()) == expected_errors, "missing name property"
