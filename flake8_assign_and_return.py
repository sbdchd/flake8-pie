from typing import Optional, List, NamedTuple, Iterable
from functools import partial
import ast

__version__ = "0.0.4"


class ErrorLoc(NamedTuple):
    """
    location of the lint infraction
    """

    lineno: int
    col_offset: int

    message: str
    type: "AssignAndReturnCheck"


class AssignAndReturnVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[ErrorLoc] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        run checker function and track error if found
        """
        error = is_assign_and_return(node)
        if error is not None:
            self.errors.append(error)

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
                return B781(
                    lineno=return_stmt.lineno, col_offset=return_stmt.col_offset
                )

    return None


class AssignAndReturnCheck:
    name = "flake8-assign-and-return"
    version = __version__

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree

    def run(self) -> Iterable[ErrorLoc]:
        visitor = AssignAndReturnVisitor()

        visitor.visit(self.tree)

        yield from visitor.errors


B781 = partial(
    ErrorLoc,
    message="B781: You are assinging to a variable and then returning. Instead remove the assignment and return.",
    type=AssignAndReturnCheck,
)
