"""Test helpers."""
from youtubeaio.models import YouTubeThumbnail


def get_thumbnail(resolution: str) -> YouTubeThumbnail:
    """Return mock thumbnail with resolution as url."""
    return YouTubeThumbnail(
        url=resolution,
        width=100,
        height=100,
    )
