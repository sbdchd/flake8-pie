# no-assignment-and-return [![CircleCI](https://circleci.com/gh/sbdchd/flake8-assign-and-return.svg?style=svg)](https://circleci.com/gh/sbdchd/flake8-assign-and-return) [![pypi](https://img.shields.io/pypi/v/flake8-assign-and-return.svg)](https://pypi.org/project/flake8-assign-and-return/)

> A flake8 extension that checks for assignment and return in Python


A Flake8 lint based on Clippy's
[`let_and_return`](https://rust-lang.github.io/rust-clippy/master/index.html#let_and_return)
and Microsoft's TSLint lint
[`no-unnecessary-local-variable`](https://github.com/Microsoft/tslint-microsoft-contrib).

For more info on the structure of this lint, see the [accompanying blog
post](https://steve.dignam.xyz/2018/12/16/creating-a-flake8-lint/).

## examples


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

see: `flake8_assign_and_return.py` for all the test cases


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
