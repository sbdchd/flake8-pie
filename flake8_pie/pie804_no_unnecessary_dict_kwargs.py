from __future__ import annotations

import ast
import string

from flake8_pie.base import Error

DIGITS = frozenset(string.digits)
VALID_IDENT_CHARS = DIGITS | frozenset(string.ascii_letters) | {"_"}


def is_valid_kwarg_name(name: str) -> bool:
    """
    see: https://docs.python.org/3/reference/lexical_analysis.html#identifiers
    """
    if not name:
        return False
    if name[0] in DIGITS:
        return False
    return all(c in VALID_IDENT_CHARS for c in name)


def pie804_no_dict_kwargs(node: ast.Call, errors: list[Error]) -> None:
    for kw in node.keywords:
        if (
            kw.arg is None
            and isinstance(kw.value, ast.Dict)
            and all(
                isinstance(key, ast.Str) and is_valid_kwarg_name(key.s)
                for key in kw.value.keys
            )
        ):
            errors.append(
                PIE804(lineno=kw.value.lineno, col_offset=kw.value.col_offset)
            )


def PIE804(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE804: no-unnecessary-dict-kwargs: Remove the dict and pass the kwargs directly.",
    )
