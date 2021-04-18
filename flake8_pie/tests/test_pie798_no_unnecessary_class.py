from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie798_no_unnecessary_class import PIE798
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code="""
class UserManager:
    '''
    some class
    '''

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[PIE798(lineno=2, col_offset=0)],
    ),
    ex(
        # ignore any classes inheriting from something
        code="""
class UserManager(Foo):
    '''
    some class
    '''

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore any classes with extra decorators on method
        code="""
class UserManager:
    '''
    some class
    '''

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @bar
    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore any classes with a property defined w/ type
        code="""
class UserManager:
    x: int

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore any classes with a property defined
        code="""
class UserManager:
    x = None

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore classes with self as a param
        code="""
class UserManager:
    async def foo(self) -> None:
        ...

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore classes with __init__
        code="""
class UserManager:
    def __init__(self) -> None:
        ...

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore classes with any method that takes `self`
        code="""
class UserManager:
    def foo(self) -> None:
        ...

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        # ignore classes with any method that takes `self`
        code="""
class UserManager:
    def foo(self) -> None:
        ...

    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...
""",
        errors=[],
    ),
    ex(
        code="""
'''
some class
'''

class User(NamedTuple):
    name: str

def update_user(user: User) -> None:
    ...

def sync_users() -> None:
    ...
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_no_unnecessary_class(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
