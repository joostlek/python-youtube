"""Models for YouTube API."""
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field

from async_python_youtube.const import LiveBroadcastContent

T = TypeVar("T")


class YouTubeVideoThumbnail(BaseModel):
    """Model representing a video thumbnail."""

    url: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)


class YouTubeVideoThumbnails(BaseModel):
    """Model representing video thumbnails."""

    default: YouTubeVideoThumbnail = Field(...)
    medium: YouTubeVideoThumbnail = Field(...)
    high: YouTubeVideoThumbnail = Field(...)
    standard: YouTubeVideoThumbnail = Field(...)
    maxres: YouTubeVideoThumbnail | None = Field(None)


class YouTubeVideoSnippet(BaseModel):
    """Model representing video snippet."""

    published_at: datetime = Field(..., alias="publishedAt")
    channel_id: str = Field(..., alias="channelId")
    title: str = Field(...)
    description: str = Field(...)
    thumbnails: YouTubeVideoThumbnails = Field(...)
    channel_title: str = Field(..., alias="channelTitle")
    tags: list[str] = Field(...)
    live_broadcast_content: LiveBroadcastContent = Field(
        ...,
        alias="liveBroadcastContent",
    )
    default_language: str | None = Field(None, alias="defaultLanguage")
    default_audio_language: str | None = Field(None, alias="defaultAudioLanguage")


class YouTubeVideo(BaseModel):
    """Model representing a video."""

    video_id: str = Field(..., alias="id")
    snippet: YouTubeVideoSnippet | None = None
