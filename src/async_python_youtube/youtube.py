"""The YouTube API."""

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from importlib import metadata
from typing import Any, cast

import async_timeout
from aiohttp import ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from async_python_youtube.const import HttpStatusCode
from async_python_youtube.exceptions import (
    YouTubeConnectionError,
    YouTubeError,
    YouTubeNotFoundError,
)
from async_python_youtube.helper import chunk, first
from async_python_youtube.models import YouTubeVideo

__all__ = [
    "YouTube",
]

MAX_RESULTS_FOR_VIDEO = 50


@dataclass
class YouTube:
    """YouTube API client."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "youtube.googleapis.com"
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
        error_handler: dict[int, BaseException] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to OpenSky.

        A generic method for sending/handling HTTP requests done against
        OpenSky.

        Args:
        ----
            uri: the path to call.
            data: the query parameters to add.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the API.

        Raises:
        ------
            OpenSkyConnectionError: An error occurred while communicating with
                the OpenSky API.
            OpenSkyrror: Received an unexpected response from the OpenSky API.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
            path="/youtube/v3/",
        ).joinpath(uri)

        headers = {
            "User-Agent": f"PythonOpenSky/{version}",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url.with_query(data),
                    headers=headers,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the YouTube API"
            raise YouTubeConnectionError(msg) from exception
        except ClientResponseError as exception:
            if error_handler and exception.status in error_handler:
                raise error_handler[exception.status] from exception
            msg = "Error occurred while communicating with YouTube API"
            raise YouTubeConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from the YouTube API"
            raise YouTubeError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return cast(dict[str, Any], await response.json())

    async def get_video(self, video_id: str) -> YouTubeVideo | None:
        """Get a single video."""
        return await first(self.get_videos([video_id]))

    async def get_videos(
        self,
        video_ids: list[str],
    ) -> AsyncGenerator[YouTubeVideo, None]:
        """Get a list of videos."""
        error_handler: dict[int, BaseException] = {
            HttpStatusCode.NOT_FOUND: YouTubeNotFoundError("Video not found"),
        }
        for video_chunk in chunk(video_ids, MAX_RESULTS_FOR_VIDEO):
            ids = ",".join(video_chunk)
            data = {
                "part": "snippet",
                "id": ids,
                "maxResults": MAX_RESULTS_FOR_VIDEO,
            }
            res = await self._request("videos", data=data, error_handler=error_handler)
            for item in res["items"]:
                yield YouTubeVideo.parse_obj(item)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Any:
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
