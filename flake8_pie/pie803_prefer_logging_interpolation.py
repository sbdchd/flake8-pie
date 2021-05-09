from __future__ import annotations

import ast
from functools import partial

from flake8_pie.base import Error

LOG_NAMES = {"log", "logger", "logging"}

LOG_ATTRIBUTES = {
    "warn",
    "warning",
    "critical",
    "exception",
    "info",
    "debug",
    "error",
    "danger",
    "log",
    "log",
}


# https://github.com/PyCQA/pylint/blob/fb59ed86d5e463ebfdeb5d0af8539b7a8431aa15/pylint/checkers/logging.py#L157-L159
# https://github.com/PyCQA/pylint/commit/101e06f86a95dcb05e6b48c40b6fe7eb1b9a2cdb
def pie803_prefer_logging_interpolation(node: ast.Call, errors: list[Error]) -> None:
    for argument in node.args:
        if (
            isinstance(node.func, ast.Attribute)
            and (
                (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id in LOG_NAMES
                )
                or (
                    isinstance(node.func.value, ast.Attribute)
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "self"
                )
            )
            and node.func.attr in LOG_ATTRIBUTES
        ):
            if isinstance(argument, ast.BinOp) and isinstance(argument.op, ast.Mod):
                errors.append(
                    PIE803(lineno=argument.lineno, col_offset=argument.col_offset)
                )
            if (
                isinstance(argument, ast.Call)
                and isinstance(argument.func, ast.Attribute)
                and argument.func.attr == "format"
                and isinstance(argument.func.value, ast.Str)
            ):
                errors.append(
                    PIE803(lineno=argument.lineno, col_offset=argument.col_offset)
                )

            if isinstance(argument, ast.JoinedStr) and any(
                isinstance(x, ast.FormattedValue) for x in argument.values
            ):
                errors.append(
                    PIE803(lineno=argument.lineno, col_offset=argument.col_offset)
                )


PIE803 = partial(
    Error,
    message=r"PIE803: prefer-logging-interpolation: Use lazy % formatting in logging functions.",
)
