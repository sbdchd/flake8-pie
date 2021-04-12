from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error
from flake8_pie.utils import is_if_test_func_call


def is_no_bool_condition(node: ast.If | ast.IfExp) -> Error | None:
    if is_if_test_func_call(node=node, func_name="bool"):
        return PIE788(lineno=node.test.lineno, col_offset=node.test.col_offset)
    return None


PIE788 = partial(
    Error, message="PIE788: no-bool-condition: Remove unnecessary bool() call."
)
