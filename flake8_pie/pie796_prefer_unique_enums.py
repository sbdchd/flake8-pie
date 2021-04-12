from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def _extends_enum(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Enum":
            return True
        elif (
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "enum"
            and base.attr == "Enum"
        ):
            return True
    return False


def is_prefer_unique_enum(node: ast.ClassDef) -> Error | None:
    if _extends_enum(node) and not node.decorator_list:
        return PIE796(lineno=node.lineno, col_offset=node.col_offset)
    return None


PIE796 = partial(
    Error,
    message="PIE796: prefer-unique-enums: Consider using the @enum.unique decorator.",
)
