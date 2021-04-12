from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie786_precise_exception_handler import PIE786, _has_bad_control_flow
from flake8_pie.tests.utils import Error, to_errors


@pytest.mark.parametrize(
    "try_statement,error",
    [
        (
            """
try:
    print("Hello")
except:
    raise
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except Exception:
    raise
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except (ValueError, BaseException):
    print("hello world")
    raise
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except (ValueError, BaseException):
    if x != 123:
        if y == 10:
            print("hello")
    raise
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except (ValueError, BaseException):
    if x != 123:
        raise
""",
            PIE786(lineno=4, col_offset=20),
        ),
        (
            """
try:
    print("Hello")
except ValueError:
    pass
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except (ValueError, TypeError):
    pass
""",
            None,
        ),
        (
            """
try:
    print("Hello")
except:
    pass
""",
            PIE786(lineno=4, col_offset=0),
        ),
        (
            """
try:
    print("Hello")
except BaseException:
    pass
""",
            PIE786(lineno=4, col_offset=0),
        ),
        (
            """
try:
    print("Hello")
except Exception:
    pass
""",
            PIE786(lineno=4, col_offset=0),
        ),
        (
            """
try:
    print("Hello")
except (ValueError, Exception):
    pass
""",
            PIE786(lineno=4, col_offset=20),
        ),
        (
            """
try:
    print("Hello")
except (ValueError, BaseException):
    pass
""",
            PIE786(lineno=4, col_offset=20),
        ),
        (
            """
class UserViewSet(viewsets.ModelViewSet):
    def create(self, request: Request) -> Response:
        try:
            user = serializer.save()
        except Exception:
            return Response()
""",
            PIE786(lineno=6, col_offset=8),
        ),
        (
            """
try:
    print("Hello")
except (ValueError, BaseException):
    if x != 123:
        return
    raise
""",
            PIE786(lineno=4, col_offset=20),
        ),
        (
            """
for x in my_results:
    try:
        print("Hello")
    except (ValueError, BaseException):
        if x != 123:
            if y == 10:
                continue
        raise
""",
            PIE786(lineno=5, col_offset=24),
        ),
        (
            """
for x in my_results:
    try:
        print("Hello")
    except (ValueError, BaseException):
        if x != 123:
            break
        raise
""",
            PIE786(lineno=5, col_offset=24),
        ),
        (
            """
for x in my_results:
    try:
        print("Hello")
    except (ValueError, BaseException):
        break
        raise
""",
            PIE786(lineno=5, col_offset=24),
        ),
        (
            """
for x in my_results:
    try:
        print("Hello")
    except (ValueError, BaseException):
        return
        raise
""",
            PIE786(lineno=5, col_offset=24),
        ),
    ],
)
def test_broad_except(try_statement: str, error: Error | None) -> None:
    expr = ast.parse(try_statement)
    if error is None:
        assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == []
    else:
        assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == [error]


EXPRESSIONS = [
    """
if x != 123:
    if y == 10:
        continue
raise
    """,
    """
if x != 123:
    return
raise
    """,
    """
if x != 123:
    continue
raise
    """,
]


def test_has_bad_control_flow() -> None:
    for expression in EXPRESSIONS:
        expr = ast.parse(expression)
        assert _has_bad_control_flow(expr.body) is True
