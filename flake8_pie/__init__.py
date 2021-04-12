from __future__ import annotations

import ast
from typing import Iterable

from flake8_pie.base import Error, Flake8Error
from flake8_pie.pie781_assign_and_return import is_assign_and_return
from flake8_pie.pie783_celery_explicit_names import is_celery_explicit_names
from flake8_pie.pie784_celery_crontab_args import is_celery_crontab_args
from flake8_pie.pie785_celery_require_tasks_expire import is_celery_require_tasks_expire
from flake8_pie.pie786_precise_exception_handler import is_precise_exception_handler
from flake8_pie.pie787_no_len_condition import is_no_len_condition
from flake8_pie.pie788_no_bool_condition import is_no_bool_condition
from flake8_pie.pie789_prefer_isinstance_type_compare import (
    is_prefer_isinstance_type_compare,
)
from flake8_pie.pie790_no_unnecessary_pass import is_no_unnecessary_pass
from flake8_pie.pie791_no_pointless_statements import is_no_pointless_statements
from flake8_pie.pie792_no_inherit_object import is_no_inherit_object
from flake8_pie.pie793_prefer_dataclass import is_prefer_dataclass
from flake8_pie.pie794_dupe_class_field_definitions import (
    is_dupe_class_field_definition,
)
from flake8_pie.pie795_prefer_stdlib_enums import is_prefer_stdlib_enums
from flake8_pie.pie796_prefer_unique_enums import is_prefer_unique_enum
from flake8_pie.pie797_no_unnecessary_if_expr import is_no_unnecessary_if_expr


class Flake8PieVisitor(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.errors: list[Error] = []
        self.filename = filename
        self.inside_inheriting_cls_stack: list[bool] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # TODO(sbdchd): rename all these functions to `check_$number_$name` and
        # have them return a list or maybe take in the list and mutate it
        error = is_assign_and_return(node)
        if error:
            self.errors.append(error)

        error = is_celery_explicit_names(node)
        if error:
            self.errors.append(error)

        error = is_no_unnecessary_pass(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:

        error = is_no_unnecessary_pass(node)
        if error:
            self.errors.append(error)

        self.errors += is_dupe_class_field_definition(node)

        error = is_no_inherit_object(node)
        if error:
            self.errors.append(error)

        error = is_prefer_dataclass(node, self.inside_inheriting_cls_stack)
        if error:
            self.errors.append(error)

        error = is_prefer_stdlib_enums(node, self.inside_inheriting_cls_stack)
        if error:
            self.errors.append(error)

        error = is_prefer_unique_enum(node)
        if error:
            self.errors.append(error)

        is_inheriting_cls = len(node.bases) > 0
        self.inside_inheriting_cls_stack.append(is_inheriting_cls)
        self.generic_visit(node)
        self.inside_inheriting_cls_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        error = is_celery_crontab_args(node)
        if error:
            self.errors.append(error)

        error = is_celery_require_tasks_expire(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        error = is_celery_require_tasks_expire(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        error = is_precise_exception_handler(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        error = is_no_pointless_statements(node)
        if error:
            self.errors.append(error)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        error = is_no_len_condition(node)
        if error:
            self.errors.append(error)

        error = is_prefer_isinstance_type_compare(node)
        if error:
            self.errors.append(error)

        error = is_no_bool_condition(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        error = is_no_len_condition(node)
        if error:
            self.errors.append(error)

        error = is_no_bool_condition(node)
        if error:
            self.errors.append(error)

        error = is_prefer_isinstance_type_compare(node)
        if error:
            self.errors.append(error)

        error = is_no_unnecessary_if_expr(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: errors={self.errors}>"


class Flake8PieCheck:
    name = "flake8-pie"
    version = "0.6.1"

    def __init__(
        self, tree: ast.Module, filename: str, *args: object, **kwargs: object
    ) -> None:
        self.filename = filename
        self.tree = tree

    def run(self) -> Iterable[Flake8Error]:
        # When using flake8-pyi, skip the stub files.
        if self.filename.endswith(".pyi"):
            return

        visitor = Flake8PieVisitor(self.filename)
        visitor.visit(self.tree)

        for err in visitor.errors:
            yield Flake8Error(
                message=err.message,
                type=Flake8PieCheck,
                lineno=err.lineno,
                col_offset=err.col_offset,
            )
