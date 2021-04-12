from __future__ import annotations

import ast
from functools import partial
from typing import Any, cast

from flake8_pie.base import Error

BAD_EXCEPT_IDS = {"BaseException", "Exception"}


def _is_bad_except_type(except_type: ast.Name | None) -> bool:
    return except_type is None or except_type.id in BAD_EXCEPT_IDS


def _has_bad_control_flow(nodes: list[ast.stmt]) -> bool:
    """
    Check if `return`, `break` or `continue` exists in node tree.

    We allow broad exceptions when `raise` is in the except handler body, unless
    `raise` is not always called, like when there is a return, break, or
    continue in the handler body.
    """
    for node in nodes:
        if isinstance(node, (ast.Continue, ast.Break, ast.Return)):
            return True
        if (
            hasattr(node, "body")
            and isinstance(cast(Any, node).body, list)
            and _has_bad_control_flow(cast(Any, node).body)
        ):
            return True
    return False


def _body_has_raise(except_body: list[ast.stmt]) -> bool:
    for node in except_body:
        if isinstance(node, ast.Raise):
            return True
    return False


def pie786_precise_exception_handler(
    node: ast.ExceptHandler, errors: list[Error]
) -> None:
    """
    ensure try...except is not called with Exception, BaseException, or no argument
    """
    if _body_has_raise(node.body) and not _has_bad_control_flow(node.body):
        return None
    if isinstance(node.type, ast.Tuple):
        for elt in node.type.elts:
            if (isinstance(elt, ast.Name) or elt is None) and _is_bad_except_type(elt):
                errors.append(PIE786(lineno=elt.lineno, col_offset=elt.col_offset))
                return
    if (isinstance(node.type, ast.Name) or node.type is None) and _is_bad_except_type(
        node.type
    ):
        errors.append(PIE786(lineno=node.lineno, col_offset=node.col_offset))


PIE786 = partial(Error, message="PIE786: Use precise exception handlers.")
