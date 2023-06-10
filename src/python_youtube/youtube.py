"""The YouTube API."""
__all__ = [
    "YouTube",
]


class YouTube:
    """YouTube API client."""

    def __init__(self) -> None:
        """Initialize the YouTube client."""
        self.test = "ack"

    def syn(self) -> str:
        """Test method."""
        return self.test

    def ack(self) -> str:
        """Test method."""
        return self.test
