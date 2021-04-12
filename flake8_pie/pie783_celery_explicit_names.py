from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


def has_name_kwarg(dec: ast.Call) -> bool:
    return any(k.arg == "name" for k in dec.keywords)


CELERY_SHARED_TASK_NAME = "shared_task"
CELERY_TASK_NAME = "task"


def is_celery_explicit_names(func: ast.FunctionDef) -> Error | None:
    """
    check if a Celery task definition is missing an explicit name.
    """
    if func.decorator_list:
        for dec in func.decorator_list:
            if (
                isinstance(dec, ast.Attribute)
                and isinstance(dec.value, ast.Name)
                and dec.attr == CELERY_TASK_NAME
            ):
                return PIE783(lineno=dec.lineno, col_offset=dec.col_offset)
            if isinstance(dec, ast.Name) and dec.id == CELERY_SHARED_TASK_NAME:
                return PIE783(lineno=dec.lineno, col_offset=dec.col_offset)
            if isinstance(dec, ast.Call):
                if (
                    isinstance(dec.func, ast.Name)
                    and dec.func.id == CELERY_SHARED_TASK_NAME
                    and not has_name_kwarg(dec)
                ):
                    return PIE783(lineno=dec.lineno, col_offset=dec.col_offset)
                if (
                    isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == CELERY_TASK_NAME
                    and not has_name_kwarg(dec)
                ):
                    return PIE783(lineno=dec.lineno, col_offset=dec.col_offset)
    return None


PIE783 = partial(Error, message="PIE783: Celery tasks should have explicit names.")
