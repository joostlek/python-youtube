"""Models for YouTube API."""
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field

from youtubeaio.const import LiveBroadcastContent

__all__ = [
    "YouTubeThumbnail",
    "YouTubeVideoThumbnails",
    "YouTubeVideoSnippet",
    "YouTubeVideo",
    "YouTubeChannelThumbnails",
    "YouTubeChannelRelatedPlaylists",
    "YouTubeChannelContentDetails",
    "YouTubeChannelSnippet",
    "YouTubeChannel",
]

T = TypeVar("T")


class YouTubeThumbnail(BaseModel):
    """Model representing a video thumbnail."""

    url: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)


class YouTubeVideoThumbnails(BaseModel):
    """Model representing video thumbnails."""

    default: YouTubeThumbnail = Field(...)
    medium: YouTubeThumbnail = Field(...)
    high: YouTubeThumbnail = Field(...)
    standard: YouTubeThumbnail = Field(...)
    maxres: YouTubeThumbnail | None = Field(None)


class YouTubeVideoSnippet(BaseModel):
    """Model representing video snippet."""

    published_at: datetime = Field(..., alias="publishedAt")
    channel_id: str = Field(..., alias="channelId")
    title: str = Field(...)
    description: str = Field(...)
    thumbnails: YouTubeVideoThumbnails = Field(...)
    channel_title: str = Field(..., alias="channelTitle")
    tags: list[str] = Field([])
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


class YouTubeChannelThumbnails(BaseModel):
    """Model representing channel thumbnails."""

    default: YouTubeThumbnail = Field(...)
    medium: YouTubeThumbnail = Field(...)
    high: YouTubeThumbnail = Field(...)


class YouTubeChannelRelatedPlaylists(BaseModel):
    """Model representing related playlists of a channel."""

    likes: str = Field(...)
    uploads: str = Field(...)


class YouTubeChannelContentDetails(BaseModel):
    """Model representing content details of a channel."""

    related_playlists: YouTubeChannelRelatedPlaylists = Field(
        ...,
        alias="relatedPlaylists",
    )


class YouTubeChannelSnippet(BaseModel):
    """Model representing channel snippet."""

    title: str = Field(...)
    description: str = Field(...)
    published_at: datetime = Field(..., alias="publishedAt")
    thumbnails: YouTubeChannelThumbnails = Field(...)
    default_language: str | None = Field(None, alias="defaultLanguage")


class YouTubeChannel(BaseModel):
    """Model representing a YouTube channel."""

    channel_id: str = Field(..., alias="id")
    snippet: YouTubeChannelSnippet | None = None
    content_details: YouTubeChannelContentDetails | None = Field(
        None,
        alias="contentDetails",
    )

    @property
    def upload_playlist_id(self) -> str:
        """Return playlist id with uploads from channel."""
        return self.channel_id.replace("UC", "UU", 1)


class YouTubeSubscriptionSnippet(BaseModel):
    """Model representing a YouTube subscription snippet."""

    title: str = Field(...)
    description: str = Field(...)
    subscribed_at: datetime = Field(..., alias="publishedAt")
    channel_info: dict[str, str] = Field(..., alias="resourceId")

    @property
    def channel_id(self) -> str:
        """Return channel id."""
        return self.channel_info["channelId"]


class YouTubeSubscription(BaseModel):
    """Model representing a YouTube subscription."""

    subscription_id: str = Field(..., alias="id")
    snippet: YouTubeSubscriptionSnippet | None = None
