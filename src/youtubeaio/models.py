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

from youtubeaio.types import PartMissingError

T = TypeVar("T")


class YouTubeThumbnail(BaseModel):
    """Model representing a video thumbnail."""

    url: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)


class YouTubeVideoThumbnails(BaseModel):
    """Model representing video thumbnails."""

    default: YouTubeThumbnail = Field(...)
    medium: YouTubeThumbnail | None = Field(None)
    high: YouTubeThumbnail | None = Field(None)
    standard: YouTubeThumbnail | None = Field(None)
    maxres: YouTubeThumbnail | None = Field(None)

    def get_highest_quality(self) -> YouTubeThumbnail:
        """Return the highest quality thumbnail."""
        for size in (self.maxres, self.standard, self.high, self.medium):
            if size is not None:
                return size
        return self.default


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
    nullable_snippet: YouTubeVideoSnippet | None = Field(None, alias="snippet")

    @property
    def snippet(self) -> YouTubeVideoSnippet:
        """Return snippet."""
        if self.nullable_snippet is None:
            raise PartMissingError
        return self.nullable_snippet


class YouTubeChannelThumbnails(BaseModel):
    """Model representing channel thumbnails."""

    default: YouTubeThumbnail = Field(...)
    medium: YouTubeThumbnail | None = Field(None)
    high: YouTubeThumbnail | None = Field(None)

    def get_highest_quality(self) -> YouTubeThumbnail:
        """Return the highest quality thumbnail."""
        for size in (self.high, self.medium):
            if size is not None:
                return size
        return self.default


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


class YouTubeChannelStatistics(BaseModel):
    """Model representing statistics of a channel."""

    view_count: int = Field(..., alias="viewCount")
    subscriber_count: int = Field(..., alias="subscriberCount")
    subscriber_count_hidden: bool = Field(..., alias="hiddenSubscriberCount")
    video_count: int = Field(..., alias="videoCount")


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
    nullable_snippet: YouTubeChannelSnippet | None = Field(None, alias="snippet")
    nullable_content_details: YouTubeChannelContentDetails | None = Field(
        None,
        alias="contentDetails",
    )
    nullable_statistics: YouTubeChannelStatistics | None = Field(
        None,
        alias="statistics",
    )

    @property
    def upload_playlist_id(self) -> str:
        """Return playlist id with uploads from channel."""
        return str(self.channel_id).replace("UC", "UU", 1)

    @property
    def snippet(self) -> YouTubeChannelSnippet:
        """Return snippet."""
        if self.nullable_snippet is None:
            raise PartMissingError
        return self.nullable_snippet

    @property
    def content_details(self) -> YouTubeChannelContentDetails:
        """Return content details."""
        if self.nullable_content_details is None:
            raise PartMissingError
        return self.nullable_content_details

    @property
    def statistics(self) -> YouTubeChannelStatistics:
        """Return statistics."""
        if self.nullable_statistics is None:
            raise PartMissingError
        return self.nullable_statistics


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
    nullable_snippet: YouTubeSubscriptionSnippet | None = Field(None, alias="snippet")

    @property
    def snippet(self) -> YouTubeSubscriptionSnippet:
        """Return snippet."""
        if self.nullable_snippet is None:
            raise PartMissingError
        return self.nullable_snippet


class YouTubePlaylistItemSnippet(BaseModel):
    """Model representing a YouTube playlist item snippet."""

    added_at: datetime = Field(..., alias="publishedAt")
    title: str = Field(...)
    description: str = Field(...)
    thumbnails: YouTubeVideoThumbnails = Field(...)
    playlist_id: str = Field(..., alias="playlistId")


class YouTubePlaylistItemContentDetails(BaseModel):
    """Model representing a YouTube playlist item content details."""

    video_id: str = Field(..., alias="videoId")


class YouTubePlaylistItem(BaseModel):
    """Model representing a YouTube playlist item."""

    playlist_item_id: str = Field(..., alias="id")
    nullable_snippet: YouTubePlaylistItemSnippet | None = Field(None, alias="snippet")
    nullable_content_details: YouTubePlaylistItemContentDetails | None = Field(
        None,
        alias="contentDetails",
    )

    @property
    def snippet(self) -> YouTubePlaylistItemSnippet:
        """Return snippet."""
        if self.nullable_snippet is None:
            raise PartMissingError
        return self.nullable_snippet

    @property
    def content_details(self) -> YouTubePlaylistItemContentDetails:
        """Return content details."""
        if self.nullable_content_details is None:
            raise PartMissingError
        return self.nullable_content_details
