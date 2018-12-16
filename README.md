# no-assignment-and-return

> An extension for flake8 which checks for assignment (`=`) then `return` in Python


A Flake8 lint based on Clippy's
[`let_and_return`](https://rust-lang.github.io/rust-clippy/master/index.html#let_and_return)
and Microsoft's TSLint lint
[`no-unnecessary-local-variable`](https://github.com/Microsoft/tslint-microsoft-contrib).

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
poetry run pytest *.py
# or with watch
poetry run ptw *.py

# typecheck
poetry run mypy .

# format
poetry run black .

# lint
poetry run flake8 .
```

## uploading a new version to [PyPi](https://pypi.org)

```shell
# build new distribution files
poetry run python setup.py sdist bdist_wheel

# upload to pypi (Note: this will ask for login credentials)
poetry run twine upload dist/*
```
