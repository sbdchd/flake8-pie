# no-assignment-and-return


## dev

```shell
# install dependencies
poetry install

# install plugin to work with flake8
poetry run python ./setup.py install

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
