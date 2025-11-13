"""Pytest configuration for Syrupy snapshot testing with Youtube extension."""

import pytest

from syrupy import SnapshotAssertion
from tests.syrupy import YoutubeSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Youtube extension."""
    return snapshot.use_extension(YoutubeSnapshotExtension)
