from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie785_celery_require_tasks_expire import PIE785
from flake8_pie.tests.utils import to_errors

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
def test_celery_require_task_expiration(code: str, expected: Error | None) -> None:
    node = ast.parse(code)
    assert isinstance(node, ast.Module)
    expected_errors = [expected] if expected else []
    assert (
        to_errors(Flake8PieCheck(node, filename="foo.py").run())
    ) == expected_errors, "missing expiration"
