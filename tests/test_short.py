"""Tests for the YouTube client."""

import aiohttp
from aresponses import ResponsesMockServer

from youtubeaio.youtube import YouTube


async def test_is_short(
    aresponses: ResponsesMockServer,
) -> None:
    """Test YouTube video id that is a short."""
    aresponses.add(
        "www.youtube.com",
        "/shorts/2YUPfsi8PF4",
        "HEAD",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        response = await youtube.is_short("2YUPfsi8PF4")
        assert response
        await youtube.close()


async def test_is_not_short(
    aresponses: ResponsesMockServer,
) -> None:
    """Test YouTube video id that is not a short."""
    aresponses.add(
        "www.youtube.com",
        "/shorts/KXaMtA6kWXU",
        "HEAD",
        aresponses.Response(
            status=303,
            headers={
                "Content-Type": "application/binary",
                "Location": "https://www.youtube.com/watch?v=KXaMtA6kWXU",
            },
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        response = await youtube.is_short("KXaMtA6kWXU")
        assert not response
        await youtube.close()
