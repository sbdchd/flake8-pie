from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie791_no_pointless_statements import PIE791
from flake8_pie.tests.utils import ex, to_errors


@pytest.mark.parametrize(
    "code,errors",
    [
        ex(
            code="""
user.is_authenticated() is True
""",
            errors=[PIE791(lineno=2, col_offset=0)],
        ),
        ex(
            code="""
"foobar" in data
""",
            errors=[PIE791(lineno=2, col_offset=0)],
        ),
        ex(
            code="""
def test_data() -> None:
    "foobar" in data
""",
            errors=[PIE791(lineno=3, col_offset=4)],
        ),
        ex(
            code="""
def test_data() -> None:
    res.status_code == status.HTTP_200_OK
""",
            errors=[PIE791(lineno=3, col_offset=4)],
        ),
        ex(
            code="""
res.json() == []
""",
            errors=[PIE791(lineno=2, col_offset=0)],
        ),
        ex(
            code="""
class Foo:
    def __init__(self) -> None:
        super()
""",
            errors=[PIE791(lineno=4, col_offset=8)],
        ),
        ex(
            code="""
is_eql = res.json() == []
""",
            errors=[],
        ),
        ex(
            code="""
user.is_valid_user()
""",
            errors=[],
        ),
        ex(
            code="""
data = "foo"
""",
            errors=[],
        ),
        ex(
            code="""
process(data == "foo")
""",
            errors=[],
        ),
        ex(
            code="""
class Foo:
    def __init__(self) -> None:
        super().__init__()
""",
            errors=[],
        ),
        ex(
            code="""
class SomeView(BaseView):
    def list(self, request: Request) -> Response:
        data = (
            super()
            .get_queryset()
            .filter(x__gt=10)
        )
        return Response(data)
""",
            errors=[],
        ),
    ],
)
def test_no_pointless_statements(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
