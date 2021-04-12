from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import ErrorLoc, Flake8PieCheck, Flake8PieVisitor

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


def _is_loose_crontab_call(call: ast.Call) -> ErrorLoc | None:
    """
    require that a user pass all time increments that are smaller than the
    highest one they specify.

    e.g., user passes day_of_week, then they must pass hour and minute
    """
    if isinstance(call.func, ast.Name):
        if call.func.id == "crontab":
            if _is_invalid_celery_crontab(kwargs=call.keywords):
                return PIE784(lineno=call.lineno, col_offset=call.col_offset)

    return None


class GeneralFlake8PieVisitor(Flake8PieVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        error = _is_loose_crontab_call(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)


class Flake8PieCheck784(Flake8PieCheck):
    visitor = GeneralFlake8PieVisitor


PIE784 = partial(
    ErrorLoc,
    message="PIE784: Celery crontab is missing explicit arguments.",
    type=Flake8PieCheck784,
)
