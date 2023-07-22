"""Models for YouTube API."""
from enum import Enum


class HttpStatusCode(int, Enum):
    """Enum holding http status codes."""

    NOT_FOUND = 404


class VideoPart(str, Enum):
    """Enum holding the part parameters for video requests."""

    CONTENT_DETAILS = "contentDetails"
    FILE_DETAILS = "fileDetails"
    ID = "id"
    LIVE_STREAMING_DETAILS = "liveStreamingDetails"
    LOCALIZATIONS = "localizations"
    PLAYER = "player"
    PROCESSING_DETAILS = "processingDetails"
    RECORDING_DETAILS = "recordingDetails"
    SNIPPET = "snippet"
    STATISTICS = "statistics"
    STATUS = "status"
    SUGGESTIONS = "suggestions"
    TOPIC_DETAILS = "topicDetails"


class LiveBroadcastContent(str, Enum):
    """Enum holding the liveBroadcastContent values."""

    NONE = "none"
    LIVE = "live"
    UPCOMING = "upcoming"
