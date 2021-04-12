from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def _get_target_node(stmt: ast.stmt) -> ast.Name | None:
    if isinstance(stmt, ast.Assign):
        if len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                return target
    elif isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name):
            return stmt.target
    return None


def pie794_dupe_class_field_definition(node: ast.ClassDef, errors: list[Error]) -> None:
    seen_targets: set[str] = set()
    if node.bases and node.body:
        for stmt in node.body:
            target_node = _get_target_node(stmt)
            if target_node is None:
                continue
            if target_node.id in seen_targets:
                errors.append(
                    PIE794(lineno=target_node.lineno, col_offset=target_node.col_offset)
                )
            else:
                seen_targets.add(target_node.id)


PIE794 = partial(
    Error, message="PIE794: no-dupe-class-field-defs: This field is duplicated."
)
