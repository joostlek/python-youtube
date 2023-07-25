"""Tests for the YouTube client."""
import json
from datetime import timedelta

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer
from syrupy import SnapshotAssertion

from youtubeaio.helper import first
from youtubeaio.models import YouTubeVideoThumbnails
from youtubeaio.types import PartMissingError
from youtubeaio.youtube import YouTube

from . import construct_fixture, load_fixture
from .const import YOUTUBE_URL
from .helper import get_thumbnail


async def test_fetch_video(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving a video."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(
                construct_fixture("video", ["snippet", "contentDetails"], 1),
            ),
        ),
    )
    async with aiohttp.ClientSession() as session, YouTube(session=session) as youtube:
        video = await youtube.get_video(video_id="Ks-_Mh1QhMc")
        assert video == snapshot


async def test_fetch_videos(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a list of videos."""

    async def response_handler(req: BaseRequest) -> Response:
        """Response handler for this test."""
        if "pageToken" in req.query:
            fixture = "video_response_2.json"
        else:
            fixture = "video_response_1.json"
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


async def test_fetch_single_page_video(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a page of videos."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("video_response_2.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        videos = youtube.get_videos(
            video_ids=["V4DDt30Aat4"],
        )
        video3 = await videos.__anext__()
        assert video3
        assert video3.video_id == "V4DDt30Aat4"
        with pytest.raises(StopAsyncIteration):
            await videos.__anext__()


async def test_fetch_no_videos() -> None:
    """Test retrieving no videos."""
    youtube = YouTube()
    with pytest.raises(ValueError):
        await first(youtube.get_videos(video_ids=[]))


@pytest.mark.parametrize(
    ("thumbnails", "result_url"),
    [
        (
            YouTubeVideoThumbnails(
                maxres=get_thumbnail("maxres"),
                standard=get_thumbnail("standard"),
                high=get_thumbnail("high"),
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "maxres",
        ),
        (
            YouTubeVideoThumbnails(
                maxres=None,
                standard=get_thumbnail("standard"),
                high=get_thumbnail("high"),
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "standard",
        ),
        (
            YouTubeVideoThumbnails(
                maxres=None,
                standard=None,
                high=get_thumbnail("high"),
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "high",
        ),
        (
            YouTubeVideoThumbnails(
                maxres=None,
                standard=None,
                high=None,
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "medium",
        ),
        (
            YouTubeVideoThumbnails(
                maxres=None,
                standard=None,
                high=None,
                medium=None,
                default=get_thumbnail("default"),
            ),
            "default",
        ),
    ],
)
async def test_get_hq_thumbnail(
    thumbnails: YouTubeVideoThumbnails,
    result_url: str,
) -> None:
    """Check if the highest quality thumbnail is returned."""
    assert thumbnails.get_highest_quality().url == result_url


async def test_nullable_fields(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if the fields exist when they are filled."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(
                construct_fixture("video", ["snippet", "contentDetails"], 1),
            ),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        video = await youtube.get_video(video_id="V4DDt30Aat4")
        assert video
        assert video.snippet.channel_id == "UCAuUUnT6oDeKwE6v1NGQxug"
        assert video.content_details.duration == timedelta(minutes=21, seconds=3)
        assert video.content_details.caption is True


async def test_nullable_fields_null(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if an error is thrown if a non-requested part is accessed."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/videos",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(construct_fixture("video", [], 1)),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        video = await youtube.get_video(video_id="V4DDt30Aat4")
        assert video
        with pytest.raises(PartMissingError):
            assert video.snippet.thumbnails
        with pytest.raises(PartMissingError):
            assert video.content_details
