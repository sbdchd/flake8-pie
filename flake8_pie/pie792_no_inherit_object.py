from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def pie792_no_inherit_object(node: ast.ClassDef, errors: list[Error]) -> None:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "object":
            errors.append(PIE792(lineno=base.lineno, col_offset=base.col_offset))


PIE792 = partial(
    Error,
    message="PIE792: no-inherit-object: Inheriting from object is unnecssary in python3.",
)
