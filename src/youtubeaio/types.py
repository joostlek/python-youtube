"""Type definitions."""
from enum import Enum

__all__ = [
    "AuthScope",
    "YouTubeAPIError",
    "YouTubeAuthorizationError",
    "InvalidRefreshTokenError",
    "InvalidTokenError",
    "UnauthorizedError",
    "MissingScopeError",
    "YouTubeBackendError",
    "MissingAppSecretError",
    "DeprecatedError",
    "YouTubeResourceNotFoundError",
    "ForbiddenError",
]


class AuthScope(Enum):
    """Enum of authentication scopes."""

    MANAGE = "https://www.googleapis.com/auth/youtube"
    MANAGE_MEMBERSHIPS = (
        "https://www.googleapis.com/auth/youtube.channel-memberships.creator"
    )
    FORCE_SSL = "https://www.googleapis.com/auth/youtube.force-ssl"
    READ_ONLY = "https://www.googleapis.com/auth/youtube.readonly"
    UPLOAD = "https://www.googleapis.com/auth/youtube.upload"
    PARTNER = "https://www.googleapis.com/auth/youtubepartner"
    PARTNER_AUDIT = "https://www.googleapis.com/auth/youtubepartner-channel-audit"


class YouTubeAPIError(Exception):
    """Base YouTube API exception."""


class YouTubeAuthorizationError(YouTubeAPIError):
    """Exception in the YouTube Authorization."""


class InvalidRefreshTokenError(YouTubeAPIError):
    """used User Refresh Token is invalid."""


class InvalidTokenError(YouTubeAPIError):
    """Used if an invalid token is set for the client."""


class UnauthorizedError(YouTubeAuthorizationError):
    """Not authorized to use this."""


class MissingScopeError(YouTubeAuthorizationError):
    """authorization is missing scope."""


class YouTubeBackendError(YouTubeAPIError):
    """When the YouTube API itself is down."""


class PartMissingError(YouTubeAPIError):
    """If you request a part which is not requested."""


class MissingAppSecretError(YouTubeAPIError):
    """When the app secret is not set but app authorization is attempted."""


class DeprecatedError(YouTubeAPIError):
    """If something has been marked as deprecated by the YouTube API."""


class YouTubeResourceNotFoundError(YouTubeAPIError):
    """If a requested resource was not found."""


class ForbiddenError(YouTubeAPIError):
    """If you are not allowed to do that."""
