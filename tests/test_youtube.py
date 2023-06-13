"""Tests for the YouTube client."""
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from async_python_youtube.exceptions import (
    YouTubeConnectionError,
    YouTubeError,
    YouTubeNotFoundError,
)
from async_python_youtube.helper import first
from async_python_youtube.youtube import YouTube

from . import load_fixture

YOUTUBE_URL = "youtube.googleapis.com"


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

    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session, request_timeout=1)
        with pytest.raises(YouTubeConnectionError):
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
        with pytest.raises(YouTubeNotFoundError):
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
        with pytest.raises(YouTubeConnectionError):
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
        with pytest.raises(YouTubeError):
            await youtube.get_video(video_id="Ks-_Mh1QhMc")
        await youtube.close()


async def test_fetch_video(
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
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        video = await youtube.get_video(video_id="Ks-_Mh1QhMc")
        assert video
        assert video.snippet
        assert video.snippet.published_at == datetime(
            2012,
            10,
            1,
            15,
            27,
            35,
            tzinfo=timezone.utc,
        )
        assert video.snippet.channel_id == "UCAuUUnT6oDeKwE6v1NGQxug"
        assert (
            video.snippet.title
            == "Your body language may shape who you are | Amy Cuddy"
        )
        assert (
            video.snippet.description
            == "Body language affects how others see us, but it may also change how "
            'we see ourselves. Social psychologist Amy Cuddy argues that "power '
            "posing\" -- standing in a posture of confidence, even when we don't "
            "feel confident -- can boost feelings of confidence, and might have an "
            "impact on our chances for success. (Note: Some of the findings "
            "presented in this talk have been referenced in an ongoing debate "
            "among social scientists about robustness and reproducibility. Read "
            "Amy Cuddy's response here: "
            "http://ideas.ted.com/inside-the-debate-about-power-posing-a-q-a-with"
            "-amy-cuddy/)\n\nGet TED Talks recommended just for you! Learn more at "
            "https://www.ted.com/signup.\n\nThe TED Talks channel features the "
            "best talks and performances from the TED Conference, where the "
            "world's leading thinkers and doers give the talk of their lives in 18 "
            "minutes (or less). Look for talks on Technology, Entertainment and "
            "Design -- plus science, business, global issues, the arts and "
            "more.\n\nFollow TED on Twitter: http://www.twitter.com/TEDTalks\nLike "
            "TED on Facebook: https://www.facebook.com/TED\n\nSubscribe to our "
            "channel: https://www.youtube.com/TED"
        )
        assert video.snippet.thumbnails
        assert (
            video.snippet.thumbnails.default.url
            == "https://i.ytimg.com/vi/Ks-_Mh1QhMc/default.jpg"
        )
        assert video.snippet.thumbnails.default.width == 120
        assert video.snippet.thumbnails.default.height == 90
        assert (
            video.snippet.thumbnails.medium.url
            == "https://i.ytimg.com/vi/Ks-_Mh1QhMc/mqdefault.jpg"
        )
        assert video.snippet.thumbnails.medium.width == 320
        assert video.snippet.thumbnails.medium.height == 180
        assert (
            video.snippet.thumbnails.high.url
            == "https://i.ytimg.com/vi/Ks-_Mh1QhMc/hqdefault.jpg"
        )
        assert video.snippet.thumbnails.high.width == 480
        assert video.snippet.thumbnails.high.height == 360
        assert (
            video.snippet.thumbnails.standard.url
            == "https://i.ytimg.com/vi/Ks-_Mh1QhMc/sddefault.jpg"
        )
        assert video.snippet.thumbnails.standard.width == 640
        assert video.snippet.thumbnails.standard.height == 480
        assert video.snippet.thumbnails.maxres
        assert (
            video.snippet.thumbnails.maxres.url
            == "https://i.ytimg.com/vi/Ks-_Mh1QhMc/maxresdefault.jpg"
        )
        assert video.snippet.thumbnails.maxres.width == 1280
        assert video.snippet.thumbnails.maxres.height == 720
        await youtube.close()


async def test_fetch_videos(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a list of videos."""

    async def response_handler(req: BaseRequest) -> Response:
        """Response handler for this test."""
        if req.query["id"] == "Ks-_Mh1QhMc,GvgqDSnpRQM":
            fixture = "video_response_1.json"
        else:
            fixture = "video_response_2.json"
        return aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(fixture),
        )

    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        response_handler,
        repeat=2,
    )
    with patch("async_python_youtube.youtube.MAX_RESULTS_FOR_VIDEO", 2):
        async with aiohttp.ClientSession() as session:
            youtube = YouTube(session=session)
            videos = youtube.get_videos(
                video_ids=["Ks-_Mh1QhMc", "GvgqDSnpRQM", "V4DDt30Aat4"],
            )
            video1 = await videos.__anext__()
            assert video1
            assert video1.video_id == "Ks-_Mh1QhMc"
            video2 = await videos.__anext__()
            assert video2
            assert video2.video_id == "GvgqDSnpRQM"
            video3 = await videos.__anext__()
            assert video3
            assert video3.video_id == "V4DDt30Aat4"


async def test_fetch_no_videos() -> None:
    """Test retrieving no videos."""
    youtube = YouTube()
    assert await first(youtube.get_videos(video_ids=[])) is None
