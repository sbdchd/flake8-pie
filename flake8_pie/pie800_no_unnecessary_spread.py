from __future__ import annotations

import ast

from flake8_pie.base import Error


def pie800_no_unnecessary_spread(node: ast.Dict, errors: list[Error]) -> None:
    for key, val in zip(node.keys, node.values):
        if isinstance(val, ast.Dict) and key is None:
            errors.append(PIE800(lineno=val.lineno, col_offset=val.col_offset))


def PIE800(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE800 no-unnecessary-spread: Consider inlining the dict values.",
    )
