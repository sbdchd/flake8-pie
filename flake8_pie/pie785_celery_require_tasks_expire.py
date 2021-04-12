from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor


def _is_celery_dict_task_definition(dict_: ast.Dict) -> bool:
    """
    determine whether the Dict is a Celery task definition
    """
    celery_task_dict_target_keys = {"task", "schedule"}

    # We are looking for the `task` and `schedule` keys that all celery tasks
    # configured via a Dict have
    if len(dict_.keys) >= 2:
        for key in dict_.keys:
            if isinstance(key, ast.Str):
                if key.s in celery_task_dict_target_keys:
                    celery_task_dict_target_keys.remove(key.s)
                if not celery_task_dict_target_keys:
                    return True

    return len(celery_task_dict_target_keys) == 0


CELERY_OPTIONS_KEY = "options"
CELERY_EXPIRES_KEY = "expires"


def is_celery_task_missing_expires(dict_: ast.Dict) -> ErrorLoc | None:
    """
    ensure that celery tasks have an `expires` arg
    """
    if _is_celery_dict_task_definition(dict_):
        for key, value in zip(dict_.keys, dict_.values):
            if isinstance(key, ast.Str) and key.s == CELERY_OPTIONS_KEY:
                # check that options value, a dict, has `expires` key
                if isinstance(value, ast.Dict):
                    for k in value.keys:
                        if isinstance(k, ast.Str) and k.s == CELERY_EXPIRES_KEY:
                            return None

                    return PIE785(lineno=value.lineno, col_offset=value.col_offset)
        return PIE785(lineno=dict_.lineno, col_offset=dict_.col_offset)

    return None


CELERY_APPLY_ASYNC = "apply_async"


def is_celery_apply_async_missing_expires(node: ast.Call) -> ErrorLoc | None:
    """
    ensure foo.apply_async() is given an expiration
    """
    if isinstance(node.func, ast.Attribute) and node.func.attr == CELERY_APPLY_ASYNC:
        for k in node.keywords:
            if k.arg == CELERY_EXPIRES_KEY:
                return None
        return PIE785(lineno=node.lineno, col_offset=node.col_offset)

    return None


class GeneralFlake8PieVisitor(Flake8PieVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        error = is_celery_apply_async_missing_expires(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        error = is_celery_task_missing_expires(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)


class Flake8PieCheck785(Flake8PieCheck):
    visitor = GeneralFlake8PieVisitor


PIE785 = partial(
    ErrorLoc,
    message="PIE785: Celery tasks should have expirations.",
    type=Flake8PieCheck785,
)
