"""Tests for the YouTube client."""

import aiohttp
import pytest

from async_python_youtube.types import AuthScope, MissingScopeError
from async_python_youtube.youtube import YouTube


async def test_user_authentication() -> None:
    """Test setting user authentication."""
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        await youtube.set_user_authentication("token", [AuthScope.READ_ONLY], "refresh")
        assert youtube.get_user_auth_token() == "token"
        await youtube.close()


async def test_user_authentication_without_scopes() -> None:
    """Test setting user authentication without scopes."""
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session)
        with pytest.raises(MissingScopeError):
            await youtube.set_user_authentication("token", [], "refresh")
        await youtube.close()


async def test_user_authentication_without_refresh_token() -> None:
    """Test setting user authentication without refresh token."""
    async with aiohttp.ClientSession() as session:
        youtube = YouTube(session=session, app_id="asd", app_secret="asd")
        with pytest.raises(ValueError):
            await youtube.set_user_authentication("token", [AuthScope.READ_ONLY])
        youtube = YouTube(session=session, auto_refresh_auth=False)
        await youtube.set_user_authentication("token", [AuthScope.READ_ONLY])
        assert youtube.get_user_auth_token() == "token"
        await youtube.close()
