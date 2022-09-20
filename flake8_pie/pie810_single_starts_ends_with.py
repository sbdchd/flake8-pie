from __future__ import annotations

import ast
from collections import defaultdict
from functools import partial
from typing import Any, Type

from flake8_pie.base import Error


def pie810_single_starts_ends_with(node: ast.BoolOp, errors: list[Error]) -> None:
    """Check that multiple [starts/ends]with calls in an op operation do not look for
    prefixes in the same string.
    """
    if not isinstance(node.op, ast.Or):
        return

    for method in ("startswith", "endswith"):
        seen: dict[Type[ast.AST], Any] = defaultdict(set)
        for val_node in node.values:
            if (
                isinstance(val_node, ast.Call)
                and isinstance(val_node.func, ast.Attribute)
                and val_node.func.attr == method
                and isinstance(val_node.func.value, ast.Name)
            ):
                if val_node.func.value.id == "str":
                    # str.startswith(stack, needle) -> stack
                    arg = val_node.args[0]
                else:
                    # stack.startswith(needle) -> stack
                    arg = val_node.func.value

                if not isinstance(arg, (ast.Constant, ast.Name)):
                    # we cannot check the equivalence of other types
                    continue

                t = type(arg)
                val = arg.value if isinstance(arg, ast.Constant) else arg.id
                if val in seen[t]:
                    errors.append(
                        PIE810(lineno=node.lineno, col_offset=node.col_offset)
                    )
                seen[t].add(val)


PIE810 = partial(
    Error,
    message=(
        "PIE810 single-starts-ends-with: Call [starts/ends]with once with a tuple "
        "instead of calling it multiple times with the same string."
    ),
)
