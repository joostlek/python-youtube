"""Oauth helpers for YouTube."""
import aiohttp

from async_python_youtube.helper import YOUTUBE_AUTH_TOKEN_URL, build_url
from async_python_youtube.types import InvalidRefreshTokenError, UnauthorizedError

__all__ = ["refresh_access_token"]


async def refresh_access_token(
    refresh_token: str,
    app_id: str,
    app_secret: str,
    session: aiohttp.ClientSession | None = None,
) -> tuple[str, str]:
    """Refresh a user access token.

    :param str refresh_token: the current refresh_token
    :param str app_id: the id of your app
    :param str app_secret: the secret key of your app
    :param ~aiohttp.ClientSession session: optionally a active client session to be
    used for the web request to avoid having to open a new one
    :return: access_token, refresh_token
    :raises ~async_python_youtube.types.InvalidRefreshTokenException: if refresh token
    is invalid
    :raises ~async_python_youtube.types.UnauthorizedException: if both refresh and
    access token are invalid (e.g. if the user changes their password of the app gets
    disconnected)
    :rtype: (str, str)
    """
    param = {
        "refresh_token": refresh_token,
        "client_id": app_id,
        "grant_type": "refresh_token",
        "client_secret": app_secret,
    }
    url = build_url(YOUTUBE_AUTH_TOKEN_URL, {})
    ses = session if session is not None else aiohttp.ClientSession()
    async with ses.post(url, data=param) as result:
        data = await result.json()
    if session is None:
        await ses.close()
    if data.get("status", 200) == 400:
        raise InvalidRefreshTokenError(data.get("message", ""))
    if data.get("status", 200) == 401:
        raise UnauthorizedError(data.get("message", ""))
    return data["access_token"], data["refresh_token"]
