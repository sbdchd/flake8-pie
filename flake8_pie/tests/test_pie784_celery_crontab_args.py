from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie784_celery_crontab_args import PIE784, _is_invalid_celery_crontab
from flake8_pie.tests.utils import to_errors


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
def test_celery_crontab_named_args(code: str, expected: Error | None) -> None:
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
        to_errors(Flake8PieCheck(node, filename="foo.py").run())
    ) == expected_errors, "missing a required argument"


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
def test_invalid_celery_crontab_kwargs(args: list[str], expected: bool) -> None:
    kwargs = [ast.keyword(arg=arg, value=ast.Str(s="0,1")) for arg in args]
    assert _is_invalid_celery_crontab(kwargs=kwargs) == expected
