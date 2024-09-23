"""Tests for the YouTube client."""

import json

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from youtubeaio.types import PartMissingError
from youtubeaio.youtube import YouTube

from . import construct_fixture, load_fixture
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


async def test_nullable_fields(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if the fields exist when they are filled."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/subscriptions",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(construct_fixture("subscription", ["snippet"], 1)),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for subscription in youtube.get_user_subscriptions():
            assert subscription
            assert subscription.snippet


async def test_nullable_fields_null(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if an error is thrown if a non-requested part is accessed."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/subscriptions",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(construct_fixture("subscription", [], 1)),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for subscription in youtube.get_user_subscriptions():
            assert subscription
            with pytest.raises(PartMissingError):
                assert subscription.snippet.channel_id
