"""Tests for the YouTube client."""

import aiohttp
from aresponses import ResponsesMockServer

from youtubeaio.youtube import YouTube

from . import load_fixture
from .const import YOUTUBE_URL


async def test_fetch_user_subscriptions(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving a video."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/subscriptions?part=snippet&mine=true",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("subscription_response_snippet.json"),
        ),
        match_querystring=True,
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        count = 0
        async for subscription in youtube.get_user_subscriptions():
            count += 1
            assert subscription
            assert subscription.snippet
            assert subscription.snippet.channel_id
        assert count == 2
        await youtube.close()
