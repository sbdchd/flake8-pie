from __future__ import annotations

import ast


def is_if_test_func_call(*, node: ast.If | ast.IfExp, func_name: str) -> bool:
    return (
        isinstance(node.test, ast.Call)
        and isinstance(node.test.func, ast.Name)
        and node.test.func.id == func_name
    ) or (
        isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and isinstance(node.test.operand, ast.Call)
        and isinstance(node.test.operand.func, ast.Name)
        and node.test.operand.func.id == func_name
    )
