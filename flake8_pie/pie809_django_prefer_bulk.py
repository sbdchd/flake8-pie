from __future__ import annotations

import ast

from flake8_pie.base import Error


def pie809_django_prefer_bulk(
    node: ast.ListComp | ast.GeneratorExp, errors: list[Error]
) -> None:
    if (
        isinstance(node.elt, ast.Call)
        and isinstance(node.elt.func, ast.Attribute)
        and node.elt.func.attr == "create"
        and isinstance(node.elt.func.value, ast.Attribute)
        and node.elt.func.value.attr == "objects"
    ):
        errors.append(err(lineno=node.lineno, col_offset=node.col_offset))


def err(lineno: int, col_offset: int) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message="PIE809 django-prefer-bulk: bulk create multiple objects.",
    )
