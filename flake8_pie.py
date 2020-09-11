from typing import Optional, List, NamedTuple, Iterable
from functools import partial
import ast


class ErrorLoc(NamedTuple):
    """
    location of the lint infraction
    """

    lineno: int
    col_offset: int

    message: str
    type: "Flake8PieCheck"


class Flake8PieVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[ErrorLoc] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        run checker function and track error if found
        """
        error = is_assign_and_return(node)
        if error:
            self.errors.append(error)
        error = is_celery_task_missing_name(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        error = is_loose_crontab_call(node)
        if error:
            self.errors.append(error)

        error = is_celery_apply_async_missing_expires(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        error = is_celery_task_missing_expires(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        error = is_broad_except(node)
        if error:
            self.errors.append(error)

        self.generic_visit(node)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: errors={self.errors}>"


def get_assign_target_id(stmt: ast.stmt) -> Optional[str]:
    """
    We can have two types of assignments statements:
        - ast.Assign: usual assignment
        - ast.AnnAssign: assignment with a type hint

    Here we check accordingly and return the `id`.
    """
    if (
        isinstance(stmt, ast.Assign)
        and len(stmt.targets) == 1
        and isinstance(stmt.targets[0], ast.Name)
    ):
        return stmt.targets[0].id
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
        return stmt.target.id
    return None


def is_assign_and_return(func: ast.FunctionDef) -> Optional[ErrorLoc]:
    """
    check a FunctionDef for assignment and return where a user assigns to a
    variable and returns that variable instead of just returning
    """
    # assign and return can only occur with at least two statements
    if len(func.body) >= 2:
        return_stmt = func.body[-1]
        if isinstance(return_stmt, ast.Return) and isinstance(
            return_stmt.value, ast.Name
        ):
            assign_stmt = func.body[-2]
            assign_id = get_assign_target_id(assign_stmt)
            if return_stmt.value.id == assign_id:
                return PIE781(
                    lineno=return_stmt.lineno, col_offset=return_stmt.col_offset
                )

    return None


def has_name_kwarg(dec: ast.Call) -> bool:
    return any(k.arg == "name" for k in dec.keywords)


CELERY_SHARED_TASK_NAME = "shared_task"
CELERY_TASK_NAME = "task"


def is_celery_task_missing_name(func: ast.FunctionDef) -> Optional[ErrorLoc]:
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


# from: github.com/celery/celery/blob/0736cff9d908c0519e07babe4de9c399c87cb32b/celery/schedules.py#L403
CELERY_ARG_MAP = dict(minute=0, hour=1, day_of_week=2, day_of_month=3, month_of_year=4)
CELERY_LS = ["minute", "hour", "day_of_week", "day_of_month", "month_of_year"]


def is_invalid_celery_crontab(*, kwargs: List[ast.keyword]) -> bool:
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


def is_loose_crontab_call(call: ast.Call) -> Optional[ErrorLoc]:
    """
    require that a user pass all time increments that are smaller than the
    highest one they specify.

    e.g., user passes day_of_week, then they must pass hour and minute
    """
    if isinstance(call.func, ast.Name):
        if call.func.id == "crontab":
            if is_invalid_celery_crontab(kwargs=call.keywords):
                return PIE784(lineno=call.lineno, col_offset=call.col_offset)

    return None


def is_celery_dict_task_definition(dict_: ast.Dict) -> bool:
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


def is_celery_task_missing_expires(dict_: ast.Dict) -> Optional[ErrorLoc]:
    """
    ensure that celery tasks have an `expires` arg
    """
    if is_celery_dict_task_definition(dict_):
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


def is_celery_apply_async_missing_expires(node: ast.Call) -> Optional[ErrorLoc]:
    """
    ensure foo.apply_async() is given an expiration
    """
    if isinstance(node.func, ast.Attribute) and node.func.attr == CELERY_APPLY_ASYNC:
        for k in node.keywords:
            if k.arg == CELERY_EXPIRES_KEY:
                return None
        return PIE785(lineno=node.lineno, col_offset=node.col_offset)

    return None


BAD_EXCEPT_IDS = {"BaseException", "Exception"}


def is_bad_except_type(except_type: Optional[ast.Name]) -> bool:
    return except_type is None or except_type.id in BAD_EXCEPT_IDS


def is_broad_except(node: ast.Try) -> Optional[ErrorLoc]:
    """
    ensure try...except is not called with Exception, BaseException, or no argument
    """
    for node_handler in node.handlers:
        if isinstance(node_handler.type, ast.Tuple):
            for elt in node_handler.type.elts:
                if (isinstance(elt, ast.Name) or elt is None) and is_bad_except_type(
                    elt
                ):
                    return PIE786(lineno=elt.lineno, col_offset=elt.col_offset)
            continue
        if (
            isinstance(node_handler.type, ast.Name) or node_handler.type is None
        ) and is_bad_except_type(node_handler.type):
            return PIE786(
                lineno=node_handler.lineno, col_offset=node_handler.col_offset
            )
    return None


class Flake8PieCheck:
    name = "flake8-pie"
    version = "0.6.0"

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree

    def run(self) -> Iterable[ErrorLoc]:
        visitor = Flake8PieVisitor()

        visitor.visit(self.tree)

        yield from visitor.errors


PIE781 = partial(
    ErrorLoc,
    message="PIE781: You are assigning to a variable and then returning. Instead remove the assignment and return.",
    type=Flake8PieCheck,
)

PIE783 = partial(
    ErrorLoc,
    message="PIE783: Celery tasks should have explicit names.",
    type=Flake8PieCheck,
)

PIE784 = partial(
    ErrorLoc,
    message="PIE784: Celery crontab is missing explicit arguments.",
    type=Flake8PieCheck,
)

PIE785 = partial(
    ErrorLoc,
    message="PIE785: Celery tasks should have expirations.",
    type=Flake8PieCheck,
)
PIE786 = partial(
    ErrorLoc, message="PIE786: Use precise exception handlers.", type=Flake8PieCheck
)
