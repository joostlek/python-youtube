"""Tests for the helper module."""
from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

import pytest

from youtubeaio.helper import build_scope, build_url, chunk, first, get_duration, limit
from youtubeaio.types import AuthScope

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


async def _generator(amount: int) -> AsyncGenerator[int, None]:
    for i in range(amount):
        yield i


async def test_first() -> None:
    """Test if the first method works."""
    first_variable = await first(_generator(1))
    assert first_variable == 0


async def test_first_unavailable() -> None:
    """Test if the first method works."""
    second_variable = await first(_generator(0))
    assert second_variable is None


def test_chunk() -> None:
    """Test if the chunk method works."""
    source = list(range(10))

    result = list(chunk(source, 3))
    assert result == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]


async def test_limit() -> None:
    """Test if the limit method works."""
    async for i in limit(_generator(10), 3):
        assert i < 3
    async for i in limit(_generator(2), 3):
        assert i < 3


async def test_limit_invalid_value() -> None:
    """Test if the limit method works."""
    with pytest.raises(ValueError):
        await limit(_generator(10), 0).__anext__()


async def test_build_scope() -> None:
    """Test build scope."""
    assert (
        build_scope([AuthScope.READ_ONLY, AuthScope.MANAGE])
        == "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube"
    )


@pytest.mark.parametrize(
    ("params", "remove_none", "split_lists", "enum_value", "result"),
    [
        (
            {
                "hello": None,
            },
            True,
            True,
            True,
            "asd.com",
        ),
        (
            {
                "hello": None,
            },
            False,
            True,
            True,
            "asd.com?hello",
        ),
        (
            {
                "hello": [
                    "yes",
                    "no",
                ],
            },
            False,
            True,
            True,
            "asd.com?hello=yes&hello=no",
        ),
        (
            {
                "hello": [
                    "yes",
                    "no",
                ],
            },
            False,
            False,
            True,
            "asd.com?hello=%5B%27yes%27%2C%20%27no%27%5D",
        ),
        (
            {
                "hello": AuthScope.MANAGE,
            },
            False,
            True,
            True,
            "asd.com?hello=https%3A//www.googleapis.com/auth/youtube",
        ),
        (
            {
                "hello": AuthScope.MANAGE,
            },
            False,
            False,
            False,
            "asd.com?hello=AuthScope.MANAGE",
        ),
    ],
    ids=[
        "None value removed",
        "None value",
        "Split list",
        "Non split list",
        "Enum value",
        "Non enum value",
    ],
)
async def test_build_url(
    params: dict[str, Any],
    remove_none: bool,
    split_lists: bool,
    enum_value: bool,
    result: str,
) -> None:
    """Test build url."""
    assert build_url("asd.com", params, remove_none, split_lists, enum_value) == result


@pytest.mark.parametrize(
    ("duration", "result"),
    [
        (
            "PT5S",
            timedelta(seconds=5),
        ),
        (
            "PT10M5S",
            timedelta(minutes=10, seconds=5),
        ),
        (
            "PT2H10M5S",
            timedelta(hours=2, minutes=10, seconds=5),
        ),
        (
            "P4DT2H10M5S",
            timedelta(days=4, hours=2, minutes=10, seconds=5),
        ),
    ],
)
def test_duration(
    duration: str,
    result: timedelta,
) -> None:
    """Test duration,."""
    assert get_duration(duration) == result
