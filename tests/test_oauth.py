"""Tests for the YouTube client."""

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from youtubeaio.oauth import refresh_access_token
from youtubeaio.types import InvalidRefreshTokenError, UnauthorizedError

from . import load_fixture


async def test_refresh_access_token(
    aresponses: ResponsesMockServer,
) -> None:
    """Test setting user authentication."""

    async def response_handler(request: BaseRequest) -> Response:
        """Response handler for this test."""
        assert (
            await request.text()
            == "refresh_token=asdasd&client_id=app_id&grant_type=refresh_token&"
            "client_secret=app_secret&access_type=offline&prompt=consent"
        )
        return aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("refresh_token.json"),
        )

    aresponses.add(
        "oauth2.googleapis.com",
        "/token",
        "POST",
        response_handler,
    )
    async with aiohttp.ClientSession() as session:
        await refresh_access_token("asdasd", "app_id", "app_secret", session)


async def test_refresh_access_token_new_session(
    aresponses: ResponsesMockServer,
) -> None:
    """Test setting user authentication with new session."""
    aresponses.add(
        "oauth2.googleapis.com",
        "/token",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("refresh_token.json"),
        ),
    )
    await refresh_access_token("asdasd", "app_id", "app_secret")


async def test_refresh_access_token_invalid_token(
    aresponses: ResponsesMockServer,
) -> None:
    """Test setting user authentication with invalid refresh token."""
    aresponses.add(
        "oauth2.googleapis.com",
        "/token",
        "POST",
        aresponses.Response(
            status=400,
            headers={"Content-Type": "application/json"},
            text='{"error": "Invalid token"}',
        ),
    )
    with pytest.raises(InvalidRefreshTokenError):
        await refresh_access_token("asdasd", "app_id", "app_secret")


async def test_refresh_access_token_unauthorized(
    aresponses: ResponsesMockServer,
) -> None:
    """Test setting user authentication while unauthorized."""
    aresponses.add(
        "oauth2.googleapis.com",
        "/token",
        "POST",
        aresponses.Response(
            status=401,
            headers={"Content-Type": "application/json"},
            text='{"error": "Unauthorized"}',
        ),
    )
    with pytest.raises(UnauthorizedError):
        await refresh_access_token("asdasd", "app_id", "app_secret")
