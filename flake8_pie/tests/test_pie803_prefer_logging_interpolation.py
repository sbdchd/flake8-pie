from __future__ import annotations

import ast

import pytest

from flake8_pie import Flake8PieCheck
from flake8_pie.pie803_prefer_logging_interpolation import PIE803
from flake8_pie.tests.utils import Error, ex, to_errors

EXAMPLES = [
    ex(
        code=r"""
logger.info("Login error for %s" % user)
    """,
        errors=[PIE803(lineno=2, col_offset=12)],
    ),
    ex(
        code=r"""
log.warn("Login error for %s, %s" % (user_id, name))
    """,
        errors=[PIE803(lineno=2, col_offset=9)],
    ),
    ex(
        code=r"""
logging.log("Login error for {}".format(user))
    """,
        errors=[PIE803(lineno=2, col_offset=12)],
    ),
    ex(
        code=r"""
logging.log(logging.DEBUG, "Login error for {}".format(user))
    """,
        errors=[PIE803(lineno=2, col_offset=27)],
    ),
    ex(
        code=r"""
logger.debug("Login error for {}, {}".format(user_id, name))
    """,
        errors=[PIE803(lineno=2, col_offset=13)],
    ),
    ex(
        code=r"""
logger.critical(f"Login error for {user}")
    """,
        errors=[PIE803(lineno=2, col_offset=16)],
    ),
    ex(
        code=r"""
log.info(f"Login error for {user:0.2f}")
    """,
        errors=[PIE803(lineno=2, col_offset=9)],
    ),
    ex(
        code=r"""
self.logger.critical(f"Login error for {user}, {userid}")
    """,
        errors=[PIE803(lineno=2, col_offset=21)],
    ),
    ex(
        code=r"""
self.log.exception(f"Login error for")
logger.info("Login error for %s", user)
log.info("Login error for %s, %s", user_id, name)
    """,
        errors=[],
    ),
]


@pytest.mark.parametrize("code,errors", EXAMPLES)
def test_prefer_logging_interpolation(code: str, errors: list[Error]) -> None:
    expr = ast.parse(code)
    assert to_errors(Flake8PieCheck(expr, filename="foo.py").run()) == errors
