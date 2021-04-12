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


def pie786_prefer_unique_enum(node: ast.ClassDef, errors: list[Error]) -> None:
    if _extends_enum(node) and not node.decorator_list:
        seen: set[str | complex | None | bool] = set()
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if isinstance(stmt.value, ast.Num):
                    num_val = stmt.value.n
                    if num_val in seen:
                        errors.append(
                            PIE796(lineno=stmt.lineno, col_offset=stmt.col_offset)
                        )
                    else:
                        seen.add(num_val)
                elif isinstance(stmt.value, ast.Str):
                    str_val = stmt.value.s
                    if str_val in seen:
                        errors.append(
                            PIE796(lineno=stmt.lineno, col_offset=stmt.col_offset)
                        )
                    else:
                        seen.add(str_val)
                elif isinstance(stmt.value, ast.NameConstant):
                    name_val: None | bool = stmt.value.value
                    if name_val in seen:
                        errors.append(
                            PIE796(lineno=stmt.lineno, col_offset=stmt.col_offset)
                        )
                    else:
                        seen.add(name_val)


PIE796 = partial(
    Error, message="PIE796: prefer-unique-enums: Consider using removing dupe values."
)
