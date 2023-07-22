"""The YouTube API."""
import asyncio
from collections.abc import AsyncGenerator, Callable, Coroutine
from dataclasses import field
from logging import getLogger
from typing import Any, TypeVar

import async_timeout
from aiohttp import ClientResponse, ClientSession

from async_python_youtube.helper import (
    YOUTUBE_AUTH_TOKEN_URL,
    build_scope,
    build_url,
    first,
)
from async_python_youtube.models import YouTubeVideo
from async_python_youtube.types import (
    AuthScope,
    MissingAppSecretError,
    MissingScopeError,
    YouTubeAPIError,
    YouTubeAuthorizationError,
    YouTubeBackendError,
    YouTubeResourceNotFoundError,
)

__all__ = [
    "YouTube",
]
T = TypeVar("T")


class YouTube:
    """YouTube API client."""

    base_url: str = "https://youtube.googleapis.com/youtube/v3/"
    _close_session: bool = False

    logger = getLogger(__name__)

    _app_auth_token: str | None = None
    _app_auth_scopes: list[AuthScope] = field(default_factory=list)
    _has_app_auth = False
    _user_auth_token: str | None = None
    _user_auth_refresh_token: str | None = None
    _user_auth_scopes: list[AuthScope] = field(default_factory=list)
    _has_user_auth = False
    auto_refresh_auth = True

    def __init__(
        self,
        app_id: str,
        app_secret: str | None = None,
        authenticate_app: bool = True,
        target_app_auth_scope: list[AuthScope] | None = None,
        session: ClientSession | None = None,
        session_timeout: int = 10,
    ) -> None:
        """Initialize YouTube object."""
        self.session = session
        self.session_timeout = session_timeout
        self.app_id = app_id
        self.app_secret = app_secret
        self._authenticate_app = authenticate_app
        self._target_app_scope = target_app_auth_scope
        self._r_lookup: dict[
            str,
            Callable[
                [ClientSession, str, dict[str, Any] | None],
                Coroutine[Any, Any, ClientResponse],
            ],
        ] = {
            "get": self._api_get_request,
        }

    async def _check_request_return(self, response: ClientResponse) -> ClientResponse:
        if response.status == 500:
            msg = "Internal Server Error"
            raise YouTubeBackendError(msg)
        if response.status == 400:
            msg = (await response.json()).get("message")
            raise YouTubeAPIError(
                "Bad Request" + ("" if msg is None else f" - {msg!s}"),
            )
        if response.status == 404:
            raise YouTubeResourceNotFoundError
        if 400 <= response.status < 500:
            raise YouTubeAPIError
        return response

    async def _api_get_request(
        self,
        session: ClientSession,
        url: str,
        data: dict[str, Any] | None = None,
    ) -> ClientResponse:
        """Make GET request with authorization."""
        headers = {"Authorization": f"Bearer {self._user_auth_token}"}
        self.logger.debug("making GET request to %s", url)
        response = await session.get(url, headers=headers, json=data)
        return await self._check_request_return(response)

    async def _build_generator(
        self,
        req: str,
        url: str,
        url_params: dict[str, Any],
        return_type: T,
        body_data: dict[str, Any] | None = None,
        split_lists: bool = False,
        error_handler: dict[int, BaseException] | None = None,
    ) -> AsyncGenerator[T, None]:
        method = self._r_lookup.get(req.lower())
        if method is None:
            msg = "HTTP method not found"
            raise YouTubeAPIError(msg)
        _after = url_params.get("after")
        _first = True
        if not self.session:
            self.session = ClientSession()
            self._close_session = True
        try:
            while _first or _after is not None:
                url_params["pageToken"] = _after
                _url = build_url(
                    self.base_url + url,
                    url_params,
                    remove_none=True,
                    split_lists=split_lists,
                )
                async with async_timeout.timeout(self.session_timeout):
                    response = await method(self.session, _url, body_data)
                if error_handler is not None and response.status in error_handler:
                    raise error_handler[response.status]
                if response.content_type != "application/json":
                    msg = "Unexpected response type"
                    raise YouTubeAPIError(msg)
                data = await response.json()
                for entry in data.get("items", []):
                    yield return_type(**entry)  # type: ignore[operator]
                _after = data.get("nextPageToken")
                _first = False
        except asyncio.TimeoutError as exc:
            msg = "Timeout occurred"
            raise YouTubeAPIError(msg) from exc

    async def _generate_app_token(self) -> None:
        if self.app_secret is None:
            raise MissingAppSecretError
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "client_credentials",
            "scope": build_scope(self._app_auth_scopes),
        }
        self.logger.debug("generating fresh app token")
        url = build_url(YOUTUBE_AUTH_TOKEN_URL, params)
        async with async_timeout.timeout(
            self.session_timeout
        ), ClientSession() as session:
            result = await session.post(url)
        if result.status != 200:
            msg = f"Authentication failed with code {result.status} ({result.text})"
            raise YouTubeAuthorizationError(msg)
        try:
            data = await result.json()
            self._app_auth_token = data["access_token"]
        except ValueError as exc:
            msg = "Authentication response did not have a valid json body"
            raise YouTubeAuthorizationError(msg) from exc
        except KeyError as exc:
            msg = "Authentication response did not contain access_token"
            raise YouTubeAuthorizationError(msg) from exc

    async def authenticate_app(self, scopes: list[AuthScope]) -> None:
        """Authenticate with a fresh generated app token.

        :param scopes: List of Authorization scopes to use
        :raises ~async_python_youtube.types.YouTubeAuthorizationException:
        if the authentication fails
        :return: None
        """
        self._app_auth_scopes = scopes
        await self._generate_app_token()
        self._has_app_auth = True

    async def set_app_authentication(self, token: str, scopes: list[AuthScope]) -> None:
        """Set an app token, most likely only used for testing purposes.

        :param token: the app token
        :param scopes: List of Authorization scopes that the given app token has
        """
        self._app_auth_token = token
        self._app_auth_scopes = scopes
        self._has_app_auth = True

    async def set_user_authentication(
        self,
        token: str,
        scopes: list[AuthScope],
        refresh_token: str | None = None,
    ) -> None:
        """Set a user token to be used.

        :param token: the generated user token
        :param scopes: List of Authorization Scopes that the given user token has
        :param refresh_token: The generated refresh token, has to be provided if
        :attr:`auto_refresh_auth` is True |default| :code:`None`
        :raises ValueError: if :attr:`auto_refresh_auth` is True but refresh_token is
        not set
        :raises ~async_python_youtube.types.MissingScopeException: if given token is
         missing one of the required scopes
        :raises ~async_python_youtube.types.InvalidTokenException: if the given token
        is invalid or for a different client id
        """
        if refresh_token is None and self.auto_refresh_auth:
            msg = "refresh_token has to be provided when auto_refresh_auth is True"
            raise ValueError(msg)
        if scopes is None:
            msg = "scope was not provided"
            raise MissingScopeError(msg)

        self._user_auth_token = token
        self._user_auth_refresh_token = refresh_token
        self._user_auth_scopes = scopes
        self._has_user_auth = True

    def get_app_token(self) -> str | None:
        """Return the app token that the api uses or None when not authenticated.

        :return: app token
        """
        return self._app_auth_token

    def get_user_auth_token(self) -> str | None:
        """Return the current user auth token, None if no user Authentication is set.

        :return: current user auth token
        """
        return self._user_auth_token

    async def get_videos(
        self,
        video_ids: list[str],
    ) -> AsyncGenerator[YouTubeVideo, None]:
        """Get videos by id."""
        if not video_ids:
            msg = "at least one video id has to be set"
            raise ValueError(msg)
        param = {
            "part": "snippet",
            "id": video_ids,
        }
        async for item in self._build_generator(
            "GET",
            "videos",
            param,
            YouTubeVideo,
            split_lists=True,
        ):
            yield item  # type: ignore[misc]

    async def get_video(self, video_id: str) -> YouTubeVideo | None:
        """Get a single video."""
        return await first(self.get_videos([video_id]))

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> "YouTube":
        """Async enter.

        Returns
        -------
            The YouTube object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
