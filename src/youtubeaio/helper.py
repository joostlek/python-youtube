"""Helper functions for the YouTube API."""
import urllib.parse
from collections.abc import AsyncGenerator, Generator
from enum import Enum
from typing import Any, TypeVar

from youtubeaio.types import AuthScope

__all__ = [
    "YOUTUBE_AUTH_BASE_URL",
    "YOUTUBE_AUTH_TOKEN_URL",
    "build_scope",
    "build_url",
    "first",
    "chunk",
    "limit",
]

T = TypeVar("T")

YOUTUBE_AUTH_BASE_URL: str = "https://oauth2.googleapis.com"
YOUTUBE_AUTH_TOKEN_URL: str = f"{YOUTUBE_AUTH_BASE_URL}/token"


def build_scope(scopes: list[AuthScope]) -> str:
    """Build a valid scope string from list.

    :param scopes: list of :class:`~youtubeaio.types.AuthScope`
    :returns: the valid auth scope string
    """
    return " ".join([s.value for s in scopes])


def build_url(
    url: str,
    params: dict[str, Any],
    remove_none: bool = False,
    split_lists: bool = False,
    enum_value: bool = True,
) -> str:
    """Build a valid url string.

    :param url: base URL
    :param params: dictionary of URL parameter
    :param remove_none: if set all params that have a None value get removed
    |default| :code:`False`
    :param split_lists: if set all params that are a list will be split over multiple
    url parameter with the same name |default| :code:`False`
    :param enum_value: if true, automatically get value string from Enum values
    |default| :code:`True`
    :return: URL
    """

    def get_value(input_value: Any) -> str:
        if not enum_value:
            return str(input_value)
        if isinstance(input_value, Enum):
            return str(input_value.value)
        return str(input_value)

    def add_param(res: str, query_key: str, query_value: Any) -> str:
        if len(res) > 0:
            res += "&"
        res += query_key
        if query_value is not None:
            res += "=" + urllib.parse.quote(get_value(query_value))
        return res

    result = ""
    for key, value in params.items():
        if value is None and remove_none:
            continue
        if split_lists and isinstance(value, list):
            for val in value:
                result = add_param(result, key, val)
        else:
            result = add_param(result, key, value)
    return url + (("?" + result) if len(result) > 0 else "")


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
