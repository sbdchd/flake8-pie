from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error

# from: github.com/celery/celery/blob/0736cff9d908c0519e07babe4de9c399c87cb32b/celery/schedules.py#L403
CELERY_ARG_MAP = dict(minute=0, hour=1, day_of_week=2, day_of_month=3, month_of_year=4)
CELERY_LS = ["minute", "hour", "day_of_week", "day_of_month", "month_of_year"]


def _is_invalid_celery_crontab(*, kwargs: list[ast.keyword]) -> bool:
    keyword_args = {k.arg for k in kwargs if k.arg is not None}

    if not keyword_args:
        return True

    largest_index = max(
        (CELERY_ARG_MAP[k] for k in keyword_args if CELERY_ARG_MAP.get(k)), default=0
    )

    for key in CELERY_LS[:largest_index]:
        if key not in keyword_args:
            return True

    return False


def pie784_celery_crontab_args(call: ast.Call, errors: list[Error]) -> None:
    """
    require that a user pass all time increments that are smaller than the
    highest one they specify.

    e.g., user passes day_of_week, then they must pass hour and minute
    """
    if (
        isinstance(call.func, ast.Name)
        and call.func.id == "crontab"
        and _is_invalid_celery_crontab(kwargs=call.keywords)
    ):
        errors.append(PIE784(lineno=call.lineno, col_offset=call.col_offset))


PIE784 = partial(Error, message="PIE784: Celery crontab is missing explicit arguments.")
