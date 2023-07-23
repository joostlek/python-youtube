"""Tests for the YouTube client."""
import asyncio

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from youtubeaio.types import (
    ForbiddenError,
    UnauthorizedError,
    YouTubeAPIError,
    YouTubeBackendError,
    YouTubeResourceNotFoundError,
)
from youtubeaio.youtube import YouTube

from . import load_fixture
from .const import YOUTUBE_URL


async def test_new_session(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a video."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("video_response_snippet.json"),
        ),
    )
    async with YouTube() as youtube:
        assert not youtube.session
        await youtube.get_video(video_id="Ks-_Mh1QhMc")
        assert youtube.session


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: BaseRequest) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        response_handler,
    )

    youtube = YouTube(session_timeout=1)
    with pytest.raises(YouTubeAPIError):
        assert await youtube.get_video(video_id="Ks-_Mh1QhMc")
    await youtube.close()


async def test_fetch_video_not_found(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a non-existent video."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=404,
            headers={"Content-Type": "application/json"},
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(YouTubeResourceNotFoundError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_general_error_handling(
    aresponses: ResponsesMockServer,
) -> None:
    """Test throwing unexpected error."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=418,
            headers={"Content-Type": "application/json"},
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(YouTubeAPIError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_unexpected_server_response(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling a server error."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="Yes",
        ),
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(YouTubeAPIError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_internal_server_error(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling an internal server error."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=500,
            headers={"Content-Type": "plain/text"},
            text="Yes",
        ),
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(YouTubeBackendError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_bad_request(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling a bad request."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=400,
            headers={"Content-Type": "application/json"},
            text='{"message":"Something went wrong"}',
        ),
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(YouTubeAPIError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_unauthorized(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling being unauthorized."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=401,
            headers={"Content-Type": "application/json"},
            text='{"message":"Something went wrong"}',
        ),
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(UnauthorizedError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_not_activated(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling YouTube api not activated."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=403,
            headers={"Content-Type": "application/json"},
            text=load_fixture("youtube_not_activated.json"),
        ),
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(ForbiddenError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()
