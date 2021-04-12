from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie783_celery_explicit_names import PIE783
from flake8_pie.tests.utils import Error, to_errors


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
        (
            """
@shared_task
def foo():
    pass
""",
            PIE783(lineno=2, col_offset=1),
        ),
        (
            """
@app.task
def bar():
    pass
""",
            PIE783(lineno=2, col_offset=1),
        ),
    ],
)
def test_celery_task_name_lint(code: str, expected: Error | None) -> None:
    node = ast.parse(code)
    assert isinstance(node, ast.Module)
    expected_errors = [expected] if expected else []
    assert (
        to_errors(Flake8PieCheck(node, filename="foo.py").run()) == expected_errors
    ), "missing name property"
