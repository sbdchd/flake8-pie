# flake8-pie [![CircleCI](https://circleci.com/gh/sbdchd/flake8-pie.svg?style=svg)](https://circleci.com/gh/sbdchd/flake8-pie) [![pypi](https://img.shields.io/pypi/v/flake8-pie.svg)](https://pypi.org/project/flake8-pie/)

> A flake8 extension that implements misc. lints

## lints

### PIE781: assign-and-return

Based on Clippy's
[`let_and_return`](https://rust-lang.github.io/rust-clippy/master/index.html#let_and_return)
and Microsoft's TSLint rule
[`no-unnecessary-local-variable`](https://github.com/Microsoft/tslint-microsoft-contrib).

For more info on the structure of this lint, see the [accompanying blog
post](https://steve.dignam.xyz/2018/12/16/creating-a-flake8-lint/).

#### examples

```python
# error
def foo():
   x = bar()
   return x

# allowed
def foo():
   x, _ = bar()
   return x
```

### PIE783: celery-explicit-names

Warn about [Celery](https://pypi.org/project/celery/) task definitions that don't have explicit names.

Note: this lint is kind of naive considering any decorator with a `.task()`
method or any decorator called `shared_task()` a Celery decorator.

#### examples

```python
# error
@app.task()
def foo():
    pass

# ok
@app.task(name="app_name.tasks.foo")
def foo():
    pass
```

### PIE784: celery-explicit-crontab-args

The `crontab` class provided by Celery has some default args that are
suprising to new users. Specifically, `crontab(hour="0,12")` won't run a task
at midnight and noon, it will run the task at every minute during those two
hours. This lint makes that call an error, forcing you to write
`crontab(hour="0, 12", minute="*")`.

Additionally, the lint is a bit more complex in that it requires you specify
every smaller increment than the largest time increment you provide. So if you
provide `days_of_week`, then you need to provide `hour`s and `minute`s
explicitly.

Note: if you like the default behavior of `crontab()` then you can either
disable this lint or pass `"*"` for the `kwarg` value, e.g., `minutes="*"`.

Also, since this lint is essentially a naive search for calls to a
`crontab()` function, if you have a function named the same then this will
cause false positives.

### PIE785: celery-require-tasks-expire

Celery tasks can bunch up if they don't have expirations.

This enforces specifying expirations in both the celery beat config dict and
in `.apply_async()` calls.

The same caveat applies about how this lint is naive.

### PIE786: precise-exception-handlers

Be precise in what exceptions you catch. Bare `except:` handlers, catching `BaseException`, or catching `Exception` can lead to unexpected bugs.

#### examples

```python
# error
try:
    save_file(name="export.csv")
except:
    pass

# error
try:
    save_file(name="export.csv")
except BaseException:
    pass

# error
try:
    save_file(name="export.csv")
except Exception:
    pass

# error
try:
    save_file(name="export.csv")
except (ValueError, Exception):
    pass


# ok
try:
    save_file(name="export.csv")
except OSError:
    pass
```

### PIE787: no-len-condition

Empty collections are fasley in Python so calling `len()` is unnecessary when
checking for emptiness in an if statement/expression.

Comparing to explicit scalars is allowed.

```python
# error
if len(foo): ...
if not len(foo): ...

# ok
if foo: ...
if not foo: ...
if len(foo) > 0: ...
if len(foo) == 0: ...
```

### PIE788: no-bool-condition

If statements/expressions evalute the truthiness of the their test argument,
so calling `bool()` is unnecessary.

Comparing to `True`/`False` is allowed.

```python
# error
if bool(foo): ...
if not bool(foo): ...

# ok
if foo: ...
if not foo: ...
if bool(foo) is True: ...
if bool(foo) is False: ...
```

### PIE789: prefer-isinstance-type-compare

Using `type()` doesn't take into account subclassess and type checkers won't
refine the type, use `isinstance` instead.

```python
# error
if type(foo) == str: ...
if type(foo) is str: ...
if type(foo) in [int, str]: ...

# ok
if isinstance(foo, str): ...
if isinstance(foo, (int, str)): ...
```

### PIE790: no-unnecessary-pass

`pass` is unnecessary when definining a `class` or function with an empty
body.

```python
# error
class BadError(Exception):
    """
    some doc comment
    """
    pass

def foo() -> None:
    """
    some function
    """
    pass

# ok
class BadError(Exception):
    """
    some doc comment
    """

def foo() -> None:
    """
    some function
    """
```

### PIE791: no-pointless-statements

Comparisions without an assignment or assertion are probably a typo.

```python
# error
"foobar" in data
res.json() == []
user.is_authenticated() is True

# ok
assert "foobar" in data
foo = res.json() == []
use.is_authenticated()
```

### PIE792: no-inherit-object

Inheriting from `object` isn't necessary in Python 3.

```python
# error
class Foo(object):
    ...

# ok
class Foo:
    ...
```

### PIE793: prefer-dataclass

Attempts to find cases where the `@dataclass` decorator is unintentionally
missing.

```python
# error
class Foo:
    z: dict[int, int]
    def __init__(self) -> None: ...

class Bar:
    x: list[str]

# ok
class Bar(Foo):
    z: dict[int, int]

@dataclass
class Bar:
    x: list[str]
```

### PIE794: dupe-class-field-definitions

Finds duplicate definitions for the same field, which can occur in large ORM
model definitions.

```python
# error
class User(BaseModel):
    email = fields.EmailField()
    # ...80 more properties...
    email = fields.EmailField()

# ok
class User(BaseModel):
    email = fields.EmailField()
    # ...80 more properties...
```

### PIE795: prefer-stdlib-enums

Instead of defining various constant properties on a class, use the stdlib
enum which typecheckers support for type refinement.

```python
# error
class Foo:
    A = "A"
    B = "B"
    C = "C"

# ok
import enum
class Foo(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
```

### PIE796: prefer-unique-enums

By default the stdlib enum allows multiple field names to map to the same
value, this lint requires each enum value be unique.

```python
# error
class Foo(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "C"

# ok
class Foo(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
```

### PIE797: no-unnecessary-if-expr

Call `bool()` directly rather than reimplementing its functionality.

```python
# error
foo(is_valid=True if buzz() else False)

# ok
foo(is_valid=bool(buzz()))
```

### PIE798: no-unnecessary-class

Instead of using class to namespace functions, use a module.

```python
# error
class UserManager:
    class User(NamedTuple):
        name: str

    @classmethod
    def update_user(cls, user: User) -> None:
        ...

    @staticmethod
    def sync_users() -> None:
        ...

# ok
class User(NamedTuple):
    name: str

def update_user(user: User) -> None:
    ...

def sync_users() -> None:
    ...
```

### PIE799: prefer-col-init

Check that values are passed in when collections are created rather than
creating an empty collection and then inserting.

```python
# error
bars = []
bar = bar()
bars.append(bar)

# ok
bar = bar()
bars = [bar]

# error
s = deque()
s.append(foo)

# ok
s = deque([foo])
```

### PIE800: no-unnecessary-spread

Check for unnecessary dict unpacking.

```python
# error
{**foo, **{"bar": 10}}

# ok
{**foo, "bar": 10}
```

### PIE801: prefer-simple-return

Return boolean expressions directly instead of returning `True` and `False`.

```python
# error
def main():
    if foo > 5:
        return True
    return False

# error
def main():
    if foo > 5:
        return True
    else:
        return False

# ok
def main():
    return foo > 5
```

### PIE802: prefer-simple-any-all

Remove unnecessary comprehensions for `any` and `all`

```python
# error
any([x.id for x in bar])
all([x.id for x in bar])

# ok
all(x.id for x in bar)
any(x.id for x in bar)
any({x.id for x in bar})
```

### PIE803: prefer-logging-interpolation

Don't format strings before logging. Let `logging` interpolate arguments.

This allows Sentry to aggregate logs, prevents raising exceptions if interpolation fails, and improves performance if the log level is disabled. See ["PyCQA/pylint#1788"](https://github.com/PyCQA/pylint/issues/1788#issuecomment-461279687).

```python
# error
logger.info("Login error for %s" % user)
logger.info("Login error for %s, %s" % (user_id, name))

# error
logger.info("Login error for {}".format(user))
logger.info("Login error for {}, {}".format(user_id, name))

# error
logger.info(f"Login error for {user}")
logger.info(f"Login error for {user_id}, {name}")

# ok
logger.info("Login error for %s", user)
logger.info("Login error for %s, %s", user_id, name)
```

### PIE804: no-unnecessary-dict-kwargs

As long as the keys of the dict are valid Python identifier names, we can safely
remove the surrounding dict.

```python
# error
foo(**{"bar": True})

# ok
foo(bar=True)
foo(**buzz)
foo(**{"bar foo": True})
```

## dev

```shell
# install dependencies
poetry install

s/lint
s/test
```

### PIE805: prefer-literal

Currently only checks for byte string literals.

```python
# error
"foo".encode()

# ok
b"foo"
"😀".encode()
```

### PIE806: no-assert-except

Instead of `assert`ing and catching the exception, use an if statement.

```python
# error
try:
    assert "@" in bar
except AssertionError:
    ...

# ok
if "@" in bar:
    ...
```

### PIE807: prefer-list-builtin

`lambda: []` is equivalent to the builtin `list`

```python
# error
@dataclass
class Foo:
    foo: List[str] = field(default_factory=lambda: [])

# ok
@dataclass
class Foo:
    foo: List[str] = field(default_factory=list)
```

### PIE808: prefer-simple-range

We can leave out the first argument to `range` in some cases since the default
start position is 0.

```python
# err
range(0, 10)

# ok
range(10)
range(x, 10)
range(0, 10, x)
```

## uploading a new version to [PyPi](https://pypi.org)

```shell
# increment `Flake8PieCheck.version` and pyproject.toml `version`

# build new distribution files and upload to pypi
# Note: this will ask for login credentials
rm -rf dist && poetry publish --build
```
