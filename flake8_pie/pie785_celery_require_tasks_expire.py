from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error


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


def _is_celery_task_missing_expires(dict_: ast.Dict, errors: list[Error]) -> None:
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

                    errors.append(
                        PIE785(lineno=value.lineno, col_offset=value.col_offset)
                    )
                    return
        errors.append(PIE785(lineno=dict_.lineno, col_offset=dict_.col_offset))


CELERY_APPLY_ASYNC = "apply_async"


def _is_celery_apply_async_missing_expires(node: ast.Call, errors: list[Error]) -> None:
    """
    ensure foo.apply_async() is given an expiration
    """
    if isinstance(node.func, ast.Attribute) and node.func.attr == CELERY_APPLY_ASYNC:
        for k in node.keywords:
            if k.arg == CELERY_EXPIRES_KEY:
                return
        errors.append(PIE785(lineno=node.lineno, col_offset=node.col_offset))


def pie785_celery_require_tasks_expire(
    node: ast.Call | ast.Dict, errors: list[Error]
) -> None:
    if isinstance(node, ast.Call):
        _is_celery_apply_async_missing_expires(node, errors)
    else:
        _is_celery_task_missing_expires(node, errors)


PIE785 = partial(Error, message="PIE785: Celery tasks should have expirations.")
