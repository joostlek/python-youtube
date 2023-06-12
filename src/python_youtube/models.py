"""The YouTube API."""
from datetime import datetime

from pydantic import BaseModel, Field


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
    maxres: YouTubeVideoThumbnail = Field(...)


class YouTubeVideoSnippet(BaseModel):
    """Model representing video snippet."""

    published_at: datetime = Field(...)
    channel_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    thumbnails: dict[str, YouTubeVideoThumbnail] = Field(...)


class YouTubeVideo(BaseModel):
    """Model representing a video."""

    snippet: YouTubeVideoSnippet | None = None
