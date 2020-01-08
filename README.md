# flake8-pie [![CircleCI](https://circleci.com/gh/sbdchd/flake8-pie.svg?style=svg)](https://circleci.com/gh/sbdchd/flake8-pie) [![pypi](https://img.shields.io/pypi/v/flake8-pie.svg)](https://pypi.org/project/flake8-pie/)

> A flake8 extension that implements misc. lints

Note: flake8-pie requires Python 3.6 or greater

## lints

- PIE781: You are assigning to a variable and then returning. Instead remove the assignment and return.
- PIE782: Unnecessary f-string. You can safely remove the `f` prefix.
- PIE783: Celery tasks should have explicit names.
- PIE784: Celery crontab is missing explicit arguments.
- PIE785: Celery tasks should have expirations.

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

### PIE783: Celery tasks should have explicit names.

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

### PIE784: Celery crontab is missing explicit arguments.

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

### PIE785: Celery tasks should have expirations.

Celery tasks can bunch up if they don't have expirations.

This enforces specifying expirations in both the celery beat config dict and
in `.apply_async()` calls.

The same caveat applies about how this lint is naive.

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
# increment `Flake8PieCheck.version` and pyproject.toml `version`

# build new distribution files and upload to pypi
# Note: this will ask for login credentials
rm -rf dist && poetry publish --build
```
