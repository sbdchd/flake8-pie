from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.base import Error
from flake8_pie.pie793_prefer_dataclass import PIE793
from flake8_pie.tests.utils import ex, to_errors

PREFER_DATACLASS_EXAMPLES = [
    ex(
        code="""
class Foo:
    x: list[str] = []
    z: dict[int, int] = dict()
    def __init__(self) -> None: ...
""",
        errors=[PIE793(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
class Foo:
    def __init__(self) -> None: ...
    x: list[str] = []
    z: dict[int, int] = dict()
""",
        errors=[PIE793(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
@dataclass
class Foo:
    class Bar:
        x: list[str] = []
        x: bool = True

    x: list[Bar]
""",
        errors=[PIE793(lineno=4, col_offset=4)],
    ),
    ex(
        code="""
class Foo:
    x: list[str]
    def __init__(self) -> None: ...
""",
        errors=[PIE793(lineno=2, col_offset=0)],
    ),
    ex(
        code="""
class Foo:
    def __init__(self) -> None: ...
""",
        errors=[],
    ),
    ex(
        code="""
class FakeEnum:
    A: int = 1
    B = 2
    C = 3
""",
        errors=[],
    ),
    ex(
        code="""
@enum.unique
class FooEnum(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
""",
        errors=[],
    ),
    ex(
        code='''
class Command:
    """ Command stores information about a pymongo network command, """

    __slots__ = ["name", "coll", "db", "metrics", "tags", "query"]

    def __init__(self, name: str, db: Optional[str], coll: str) -> None:
        self.name = name
        self.coll = coll
        self.db = db
        self.query: Optional[Union[SON, Dict[str, object]]] = None
        self.metrics: Dict[str, object] = {}
        self.tags: Dict[str, object] = {}

    def __repr__(self) -> str:
        return f"Command(name={self.name},db={self.db},coll={self.coll})"
''',
        errors=[],
    ),
    ex(
        code="""
@dataclass(init=False)
class Foo:
    x: list[str] = []
    z: dict[int, int] = dict()
    def __init__(self) -> None: ...
""",
        errors=[],
    ),
    ex(
        code="""
@dataclass
class Foo:
    x: list[str]
""",
        errors=[],
    ),
    ex(
        code="""
class Foo:
    x: list[str]
    async def create(self) -> Foo:
        raise NotImplementedError
""",
        errors=[],
    ),
    ex(
        code="""
class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
""",
        errors=[],
    ),
    ex(
        code="""
@some_decorator
class Foo:
    x: list[str]
""",
        errors=[],
    ),
    ex(
        code="""
class Foo(Bar):
    foo: bool = False
    bar: str
""",
        errors=[],
    ),
    ex(
        code="""
class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ["id", "name", "email"]
""",
        errors=[],
    ),
    ex(
        code="""
class Data(pydantic.BaseModel):
    foo: bool
    bar: str

    class Config:
        orm_mode = True
""",
        errors=[],
    ),
    ex(
        code="""
class BulkSerializerTaskMixin:
    class Meta:
        list_serializer_class = BulkContactSerializerList
""",
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", PREFER_DATACLASS_EXAMPLES)
def test_prefer_dataclass(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
