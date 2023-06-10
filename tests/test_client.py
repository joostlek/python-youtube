"""Tests for the YouTube client."""
from python_youtube.youtube import YouTube


async def test_init() -> None:
    """Test if YouTube client can be created."""
    youtube = YouTube()
    assert youtube.syn() == "ack"
    assert youtube.ack() == "ack"
