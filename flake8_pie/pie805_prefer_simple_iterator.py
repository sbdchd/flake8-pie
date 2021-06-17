from __future__ import annotations

import ast
import string
from collections.abc import Iterable
from typing import NamedTuple

from typing_extensions import TypeGuard

from flake8_pie.base import Error

KNOWN_FUNCTIONS = {"items"}


def is_name_list(val: Iterable[ast.expr]) -> TypeGuard[Iterable[ast.Name]]:
    return all(isinstance(x, ast.Name) for x in val)


class UsedVarRes(NamedTuple):
    method: str
    var: str


def get_used_var(vars: Iterable[ast.Name]) -> UsedVarRes | None:
    for idx, var in enumerate(vars):
        if not var.id.startswith("_"):
            if idx == 0:
                method = "keys"
            elif idx == 1:
                method = "values"
            else:
                raise ValueError(f"Unexpected index: {idx}")

            return UsedVarRes(method=method, var=var.id)
    return None


def has_unused_var(vars: Iterable[ast.Name]) -> bool:
    return any(x.id.startswith("_") for x in vars)


def pie805_prefer_simple_iterator_for(node: ast.For, errors: list[Error]) -> None:
    if (
        isinstance(node.target, ast.Tuple)
        and len(node.target.elts) == 2
        and is_name_list(node.target.elts)
        and has_unused_var(node.target.elts)
    ):
        res = get_used_var(node.target.elts)
        if res is None:
            return

        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Attribute)
            and node.iter.func.attr == "items"
        ):
            errors.append(
                PIE805(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    suggestion=f"use `for {res.var} in foo.{res.method}()`",
                )
            )

        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "enumerate"
        ):
            errors.append(
                PIE805(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    suggestion=f"use `for {res.var} in enumerate(...)`",
                )
            )


def pie805_prefer_simple_iterator_generator(
    node: ast.GeneratorExp | ast.ListComp, errors: list[Error]
) -> None:
    for comprehension in node.generators:
        if (
            isinstance(comprehension.iter, ast.Call)
            and isinstance(comprehension.iter.func, ast.Attribute)
            and comprehension.iter.func.attr == "items"
            and isinstance(comprehension.target, ast.Tuple)
            and len(comprehension.target.elts) == 2
            and is_name_list(comprehension.target.elts)
            and has_unused_var(comprehension.target.elts)
        ):
            res = get_used_var(comprehension.target.elts)
            if res is None:
                continue
            errors.append(
                PIE805(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    suggestion=f"use `for {res.var} in foo.{res.method}()`",
                )
            )


def PIE805(lineno: int, col_offset: int, suggestion: str) -> Error:
    return Error(
        lineno=lineno,
        col_offset=col_offset,
        message=f"PIE805: prefer-simple-iterator: {suggestion}",
    )
