from __future__ import annotations

import ast
from itertools import combinations_with_replacement

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie810_single_starts_ends_with import PIE810
from flake8_pie.tests.utils import Error, ex, to_errors

STMTS = [
    "{arg}.{method}('aaa')",
    "str.{method}({arg}, 'aaa')",
    "{arg}.{method}(('aaa', 'bbb'))",
]
MTDS = ["startswith", "endswith"]
ARGS = ["foo", "bar"]

# a single expression is ok
OK_SINGLE = [
    stmt.format(arg=arg, method=method)
    for stmt in STMTS
    for method in MTDS
    for arg in ARGS
]

# no warning if binary operator is and
OK_AND = [
    f"{stmt1} and {stmt2}"
    for stmt1, stmt2 in combinations_with_replacement(OK_SINGLE, 2)
]

# no warning if we combine startswith and endswith
OK_DIFF_MTDS = [
    f"{stmt1.format(arg='foo', method='startswith')} or {stmt2.format(arg='foo', method='endswith')}"
    for stmt1, stmt2 in zip(STMTS, STMTS)
]

# different args should not result in a warning
OK_DIFF_ARGS = [
    f"{stmt1.format(arg='foo', method=method)} or {stmt2.format(arg='bar', method=method)}"
    for stmt1, stmt2 in zip(STMTS, STMTS)
    for method in MTDS
]

WARN = [
    f"{stmt1} or {stmt2}"
    for method in MTDS
    for arg in ARGS
    for stmt1, stmt2 in combinations_with_replacement(
        [stmt.format(arg=arg, method=method) for stmt in STMTS], 2
    )
]


EXAMPLES = [ex(code=code, errors=[PIE810(lineno=1, col_offset=0)]) for code in WARN] + [
    ex(code=code, errors=[])
    for code in OK_SINGLE + OK_AND + OK_DIFF_MTDS + OK_DIFF_ARGS
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_examples(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
