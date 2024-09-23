"""Tests for the YouTube client."""

import json

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from youtubeaio.types import PartMissingError
from youtubeaio.youtube import YouTube

from . import construct_fixture, load_fixture
from .const import YOUTUBE_URL


async def test_fetch_playlist_items(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving playlist items."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/playlistItems",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("playlist_item_response_snippet_content_details.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        count = 0
        async for playlist_item in youtube.get_playlist_items(
            "UU_x5XG1OV2P6uZZ5FSM9Ttw",
        ):
            count += 1
            assert playlist_item
            assert playlist_item.snippet
            assert playlist_item.content_details
        assert count == 5
        await youtube.close()


async def test_nullable_fields(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if the fields exist when they are filled."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/playlistItems",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(
                construct_fixture("playlist_item", ["snippet", "contentDetails"], 1),
            ),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for playlist_item in youtube.get_playlist_items(
            "UU_x5XG1OV2P6uZZ5FSM9Ttw",
        ):
            assert playlist_item
            assert playlist_item.snippet
            assert playlist_item.content_details


async def test_nullable_fields_null(
    aresponses: ResponsesMockServer,
) -> None:
    """Check if an error is thrown if a non-requested part is accessed."""
    aresponses.add(
        YOUTUBE_URL,
        "/youtube/v3/playlistItems",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(construct_fixture("playlist_item", [], 1)),
        ),
    )
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        async for playlist_item in youtube.get_playlist_items(
            "UU_x5XG1OV2P6uZZ5FSM9Ttw",
        ):
            assert playlist_item
            with pytest.raises(PartMissingError):
                assert playlist_item.snippet
            with pytest.raises(PartMissingError):
                assert playlist_item.content_details
