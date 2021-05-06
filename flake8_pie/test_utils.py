from flake8_pie.utils import pairwise


def test_pairwise() -> None:
    assert list(pairwise([1])) == [(1, None)]
    assert list(pairwise([])) == []
    assert list(pairwise([1, 2])) == [(1, 2), (2, None)]
    assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3), (3, None)]
