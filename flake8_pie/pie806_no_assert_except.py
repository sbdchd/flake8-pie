from __future__ import annotations

import ast

from flake8_pie.base import Error


def pie806_no_assert_except(node: ast.Try, errors: list[Error]) -> None:
    if (
        len(node.handlers) == 1
        and isinstance(node.handlers[0].type, ast.Name)
        and node.handlers[0].type.id == "AssertionError"
        and all(isinstance(x, ast.Assert) for x in node.body)
    ):
        errors.append(PIE806(lineno=node.lineno, col_offset=node.col_offset))


def PIE806(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE806 no-assert-except: Instead of asserting and catching, use an if statment.",
    )
