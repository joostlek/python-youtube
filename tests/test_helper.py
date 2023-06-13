"""Tests for the helper module."""
from collections.abc import AsyncGenerator

import pytest

from async_python_youtube.helper import chunk, first, limit


async def _generator(amount: int) -> AsyncGenerator[int, None]:
    for i in range(0, amount):
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
    source = list(range(0, 10))

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
