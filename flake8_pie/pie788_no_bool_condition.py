from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error
from flake8_pie.utils import is_if_test_func_call


def pie788_no_bool_condition(node: ast.If | ast.IfExp, errors: list[Error]) -> None:
    if is_if_test_func_call(node=node, func_name="bool"):
        errors.append(PIE788(lineno=node.test.lineno, col_offset=node.test.col_offset))


PIE788 = partial(
    Error, message="PIE788: no-bool-condition: Remove unnecessary bool() call."
)
