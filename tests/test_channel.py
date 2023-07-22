"""Tests for the YouTube client."""
from datetime import datetime, timezone

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from youtubeaio.youtube import YouTube

from . import load_fixture
from .const import YOUTUBE_URL


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
