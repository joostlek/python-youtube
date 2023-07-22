"""Tests for the YouTube client."""
import json
from datetime import datetime, timezone

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from youtubeaio.models import YouTubeChannelThumbnails
from youtubeaio.types import PartMissingError
from youtubeaio.youtube import YouTube

from . import construct_fixture, load_fixture
from .const import YOUTUBE_URL
from .helper import get_thumbnail


async def test_fetch_channel(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a channel."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/channels",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("channel_response_snippet.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        channel_generator = youtube.get_channels(
            channel_ids=["UC_x5XG1OV2P6uZZ5FSM9Ttw"],
        )
        channel = await channel_generator.__anext__()
        assert channel
        assert channel.channel_id == "UC_x5XG1OV2P6uZZ5FSM9Ttw"
        assert channel.upload_playlist_id == "UU_x5XG1OV2P6uZZ5FSM9Ttw"
        assert channel.snippet
        assert channel.snippet.published_at == datetime(
            2007,
            8,
            23,
            0,
            34,
            43,
            tzinfo=timezone.utc,
        )
        with pytest.raises(StopAsyncIteration):
            await channel_generator.__anext__()
        await youtube.close()


async def test_fetch_own_channel(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving own channel."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/channels?part=snippet&mine=true",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("channel_response_snippet.json"),
        ),
        match_querystring=True,
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        channel_generator = youtube.get_user_channels()
        channel = await channel_generator.__anext__()
        assert channel
        assert channel.snippet
        assert channel.snippet.published_at == datetime(
            2007,
            8,
            23,
            0,
            34,
            43,
            tzinfo=timezone.utc,
        )
        with pytest.raises(StopAsyncIteration):
            await channel_generator.__anext__()
        await youtube.close()


@pytest.mark.parametrize(
    ("thumbnails", "result_url"),
    [
        (
            YouTubeChannelThumbnails(
                high=get_thumbnail("high"),
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "high",
        ),
        (
            YouTubeChannelThumbnails(
                high=None,
                medium=get_thumbnail("medium"),
                default=get_thumbnail("default"),
            ),
            "medium",
        ),
        (
            YouTubeChannelThumbnails(
                high=None,
                medium=None,
                default=get_thumbnail("default"),
            ),
            "default",
        ),
    ],
)
async def test_get_hq_thumbnail(
    thumbnails: YouTubeChannelThumbnails,
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
        "/youtube/v3/channels",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(
                construct_fixture(
                    "channel",
                    ["snippet", "contentDetails", "statistics"],
                    1,
                ),
            ),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for subscription in youtube.get_user_channels():
            assert subscription
            assert subscription.snippet
            assert subscription.content_details
            assert subscription.statistics


async def test_nullable_fields_null(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if an error is thrown if a non-requested part is accessed."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/channels",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(construct_fixture("channel", [], 1)),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for subscription in youtube.get_user_channels():
            assert subscription
            with pytest.raises(PartMissingError):
                assert subscription.snippet
            with pytest.raises(PartMissingError):
                assert subscription.content_details
            with pytest.raises(PartMissingError):
                assert subscription.statistics
