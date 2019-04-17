# flake8-pie [![CircleCI](https://circleci.com/gh/sbdchd/flake8-pie.svg?style=svg)](https://circleci.com/gh/sbdchd/flake8-pie) [![pypi](https://img.shields.io/pypi/v/flake8-pie.svg)](https://pypi.org/project/flake8-pie/)

> A flake8 extension that implements misc. lints

## lints

### PIE781: Assign and Return

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

### PIE782: No Pointless F Strings

Warn about usage of f-string without templated values.

#### examples

```python
x = (
    f"foo {y}", # ok
    f"bar" # error
)
```

## dev

```shell
# install dependencies
poetry install

# install plugin to work with flake8
poetry run python setup.py install

# test
poetry run pytest
# or with watch
poetry run ptw

# typecheck
poetry run mypy *.py

# format
poetry run black .

# lint
poetry run flake8 .
```

## uploading a new version to [PyPi](https://pypi.org)

```shell
# increment `__version__` and pyproject.toml `version`

# build new distribution files
rm -rf dist && poetry run python setup.py sdist bdist_wheel

# upload to pypi (Note: this will ask for login credentials)
poetry run twine upload dist/*
```
