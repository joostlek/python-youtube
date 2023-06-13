"""Helper functions for the YouTube API."""
from collections.abc import AsyncGenerator, Generator
from typing import TypeVar

T = TypeVar("T")


async def first(generator: AsyncGenerator[T, None]) -> T | None:
    """Return the first value or None from the given AsyncGenerator."""
    try:
        return await generator.__anext__()
    except StopAsyncIteration:
        return None


def chunk(source: list[T], chunk_size: int) -> Generator[list[T], None, None]:
    """Divide the source list in chunks of given size."""
    for i in range(0, len(source), chunk_size):
        yield source[i : i + chunk_size]


async def limit(
    generator: AsyncGenerator[T, None],
    total: int,
) -> AsyncGenerator[T, None]:
    """Limit the number of entries returned from the AsyncGenerator."""
    if total < 1:
        msg = "Limit has to be an int > 1"
        raise ValueError(msg)
    count = 0
    async for item in generator:
        count += 1
        if count > total:
            break
        yield item
