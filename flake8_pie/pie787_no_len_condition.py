from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error
from flake8_pie.utils import is_if_test_func_call


def is_no_len_condition(node: ast.If | ast.IfExp) -> Error | None:
    if is_if_test_func_call(node=node, func_name="len"):
        return PIE787(lineno=node.test.lineno, col_offset=node.test.col_offset)
    return None


PIE787 = partial(
    Error,
    message="PIE787: no-len-condition: Remove len() call or compare against a scalar.",
)
