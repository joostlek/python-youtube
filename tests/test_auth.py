"""Tests for the YouTube client."""

import aiohttp
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from async_python_youtube.youtube import YouTube

from . import load_fixture

YOUTUBE_URL = "youtube.googleapis.com"


async def test_authentication(aresponses: ResponsesMockServer) -> None:
    """Test request will be sending bearer token after authentication."""

    async def response_handler(req: BaseRequest) -> Response:
        """Response handler for this test."""
        assert req.headers.get("Authorization") == "Bearer abc"
        return aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("video_response_snippet.json"),
        )

    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        response_handler,
    )

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        youtube.authenticate("abc")
        assert await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()
