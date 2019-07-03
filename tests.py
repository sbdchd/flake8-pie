import ast
from typing import Optional
import typing

import pytest

from flake8_pie import (
    PIE781,
    PIE782,
    PIE783,
    PIE784,
    PIE785,
    ErrorLoc,
    is_assign_and_return,
    Flake8PieCheck,
    is_invalid_celery_crontab,
    is_celery_dict_task_definition,
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

    assert isinstance(node, ast.Module)

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

    assert isinstance(node, ast.Module)

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
        (
            """
@foo
@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
)
@bar
def send_messages(messages):
    pass
""",
            PIE783(lineno=3, col_offset=1),
        ),
        (
            """
def foo():
    pass
""",
            None,
        ),
    ],
)
def test_celery_task_name_lint(code: str, expected: Optional[ErrorLoc]) -> None:
    node = ast.parse(code)
    assert isinstance(node, ast.Module)
    expected_errors = [expected] if expected else []
    assert list(Flake8PieCheck(node).run()) == expected_errors, "missing name property"


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            """
crontab(hour="0,12")
""",
            PIE784(lineno=2, col_offset=0),
        ),
        (
            """
crontab(hour="0,12", minute="*")
""",
            None,
        ),
        (
            """
crontab(hour="0,12", minute="*"),
""",
            None,
        ),
        (
            """
crontab(day_of_month="*", hour="0,12"),
""",
            PIE784(lineno=2, col_offset=0),
        ),
        (
            """
crontab(day_of_week="*", minute="*"),
""",
            PIE784(lineno=2, col_offset=0),
        ),
        (
            """
crontab(month_of_year="*", day_of_month="*", hour="0,12", minute="*"),
""",
            PIE784(lineno=2, col_offset=0),
        ),
        (
            """
crontab(),
""",
            PIE784(lineno=2, col_offset=0),
        ),
        (
            """
crontab(minute="*/5")
""",
            None,
        ),
    ],
)
def test_celery_crontab_named_args(code: str, expected: Optional[ErrorLoc]) -> None:
    """
    ensure we pass a explicit params to celery's crontab
    see: https://github.com/celery/celery/blob/0736cff9d908c0519e07babe4de9c399c87cb32b/celery/schedules.py#L403

    You must pass all the params below the level you are creating.
    So if you pass hour, then you must pass minutes.
    If you pass the day arg then you must provide hours and minutes, etc.

    params:  minute, hour, day_of_week, day_of_month, month_of_year
    """
    node = ast.parse(code)
    assert isinstance(node, ast.Module)
    expected_errors = [expected] if expected else []
    assert (
        list(Flake8PieCheck(node).run()) == expected_errors
    ), "missing a required argument"


# TODO(sbdchd):
# add support for beat tasks configured via hook
#    sender.add_periodic_task(
#        crontab(hour=7, minute=30, day_of_week=1),
#        test.s('Happy Mondays!'),
#    )


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            """
{
    "foo-bar": {
        "task": "foo.task.bar",
        "schedule": crontab(hour="0,12", minute=0),
        "options": {"queue": "queue"},
    }
}
""",
            PIE785(lineno=6, col_offset=19),
        ),
        (
            """
{
    "foo-bar": {
        "task": "foo.task.bar",
        "schedule": crontab(hour="0,12", minute=0),
        "options": {"queue": "queue", "expires": 3 * 60},
    }
}
""",
            None,
        ),
        (
            """
foo_task.chunks(([id] for id in list_of_ids), 10).apply_async(
    queue_name="queue", expires=3 * 60 * 60
)
""",
            None,
        ),
        (
            """
foo_task.chunks(([id] for id in list_of_ids), 10).apply_async(
    queue_name="queue"
)
""",
            PIE785(lineno=2, col_offset=0),
        ),
        (
            """
foo.apply_async(
    queue_name="queue"
)
""",
            PIE785(lineno=2, col_offset=0),
        ),
    ],
)
def test_celery_require_task_expiration(
    code: str, expected: Optional[ErrorLoc]
) -> None:
    node = ast.parse(code)
    assert isinstance(node, ast.Module)
    expected_errors = [expected] if expected else []
    assert list(Flake8PieCheck(node).run()) == expected_errors, "missing expiration"


@pytest.mark.parametrize(
    "args,expected",
    [
        ({"minute", "hour"}, False),
        ({"hour"}, True),
        ({"hour", "day_of_week"}, True),
        ({"minute", "hour", "day_of_week"}, False),
        (
            {
                "minute",
                "hour",
                "day_of_week",
                "day_of_month",
                "month_of_year",
                "another_random_arg",
            },
            False,
        ),
        ({"minute", "hour", "day_of_week", "day_of_month", "month_of_year"}, False),
    ],
)
def test_invalid_celery_crontab_kwargs(args: typing.List[str], expected: bool) -> None:
    kwargs = [ast.keyword(arg=arg, value=ast.Str(s="0,1")) for arg in args]
    assert is_invalid_celery_crontab(kwargs=kwargs) == expected


@pytest.mark.parametrize(
    "dict_,expected",
    [
        (
            """
{
    "task": "foo.task.bar",
    "schedule": 4 * 60 * 60,
    "options": {"queue": "queue"},
}
""",
            True,
        ),
        (
            """
{"task": "foo.task.bar", "schedule": 10 * 60 * 60}
""",
            True,
        ),
        (
            """
{"task": "foo.task.bar"}
""",
            False,
        ),
        (
            """
{"schedule": 1}
""",
            False,
        ),
        (
            """
{"task": "foo.task.bar", "schedule": 3 * 60, "random-key": 10}
""",
            True,
        ),
    ],
)
def test_is_celery_dict_task_definition(dict_: str, expected: bool) -> None:
    module = ast.parse(dict_)
    assert isinstance(module, ast.Module)
    expr = module.body[0]
    assert isinstance(expr, ast.Expr)
    actual_dict = expr.value
    assert isinstance(actual_dict, ast.Dict)
    assert is_celery_dict_task_definition(actual_dict) == expected
