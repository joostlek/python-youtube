"""Asynchronous Python client for the YouTube API."""


class YouTubeError(Exception):
    """Generic exception."""


class YouTubeConnectionError(YouTubeError):
    """YouTube connection exception."""


class YouTubeCoordinateError(YouTubeError):
    """YouTube coordinate exception."""


class YouTubeUnauthenticatedError(YouTubeError):
    """YouTube unauthenticated exception."""


class YouTubeNotFoundError(YouTubeError):
    """YouTube not found exception."""
