from typing import Optional, List, NamedTuple, Iterable, Tuple
from functools import partial
import ast

__version__ = "0.0.1"


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


def is_assign_and_return(func: ast.FunctionDef) -> Optional[ErrorLoc]:
    """
    check a FunctionDef for assignment and return where a user assigns to a
    variable and returns that variable instead of just returning
    """
    # assign and return can only occur with at least two statements
    if len(func.body) >= 2:
        return_stmt = func.body[-1]
        if isinstance(return_stmt, ast.Return):
            assign_stmt = func.body[-2]
            if isinstance(assign_stmt, ast.Assign):
                # only assigned to a single variable
                if len(assign_stmt.targets) == 1 and isinstance(
                    assign_stmt.targets[0], ast.Name
                ):
                    if isinstance(return_stmt.value, ast.Name):
                        # check that assigned variable is the same one being returned
                        if return_stmt.value.id == assign_stmt.targets[0].id:
                            return B781(
                                lineno=return_stmt.lineno,
                                col_offset=return_stmt.col_offset,
                            )
    return None


class AssignAndReturnCheck:
    name = "flake8-assign-and-return"
    version = __version__

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree

    def run(self) -> Iterable[Tuple]:
        visitor = AssignAndReturnVisitor()

        visitor.visit(self.tree)

        yield from visitor.errors


B781 = partial(
    ErrorLoc,
    message="B781: You are assinging to a variable and then returning. Instead remove the assignment and return.",
    type=AssignAndReturnCheck,
)


def test_is_assign_and_return() -> None:

    func_test_cases = [
        (
            """
def foo():
   x = 'bar'
   return x
""",
            B781(lineno=4, col_offset=3),
            "single assign then return of that variable is not allowed",
        ),
        (
            """
def foo():
   x, _ = bar()
   return x
""",
            None,
            "tuple assignment then return is allowed",
        ),
        (
            """
def foo():
   bar()
   return x
""",
            None,
            "function call, not assign, and just a return of something",
        ),
        (
            """
def foo():
   pass
""",
            None,
            "empty function can't assign and return",
        ),
        (
            """
def foo():
   x = "foo"
   return 1
""",
            None,
            "valid because we don't return the useless assignment",
        ),
        (
            """
def foo():
   z = "foo"
   return x
""",
            None,
            "valid as don't return the useless assignment, but we don't warn "
            "about the useless assignment since that is already handled by flake8",
        ),
    ]

    for func, expected, reason in func_test_cases:

        node = ast.parse(func)

        func_def = node.body[0]
        assert isinstance(func_def, ast.FunctionDef)
        assert is_assign_and_return(func_def) == expected, reason

        expected_errors = [expected] if expected is not None else []

        visitor = AssignAndReturnVisitor()
        visitor.visit(node)
        assert visitor.errors == expected_errors, reason

        assert list(AssignAndReturnCheck(node).run()) == expected_errors, reason
