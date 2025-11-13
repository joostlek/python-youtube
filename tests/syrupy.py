"""Tests for the YouTube client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from syrupy.extensions import AmberSnapshotExtension
from syrupy.extensions.amber import AmberDataSerializer

if TYPE_CHECKING:
    from syrupy.types import (
        PropertyFilter,
        PropertyMatcher,
        PropertyPath,
        SerializableData,
    )


class YoutubeSnapshotSerializer(AmberDataSerializer):
    """Youtube snapshot serializer for Syrupy.

    Handles special cases for Youtube data structures.
    """

    @classmethod
    def _serialize(  # pylint: disable=too-many-arguments
        cls,
        data: SerializableData,
        *,
        depth: int = 0,
        exclude: PropertyFilter | None = None,
        include: PropertyFilter | None = None,
        matcher: PropertyMatcher | None = None,
        path: PropertyPath = (),
        visited: set[Any] | None = None,
    ) -> str:
        """Pre-process data before serializing.

        This allows us to handle specific cases for
        Youtube data structures.
        """
        serializable_data = data
        if isinstance(data, BaseModel):
            serializable_data = data.model_dump()

        return super()._serialize(
            serializable_data,
            depth=depth,
            exclude=exclude,
            include=include,
            matcher=matcher,
            path=path,
            visited=visited,
        )


class YoutubeSnapshotExtension(AmberSnapshotExtension):
    """Youtube extension for Syrupy."""

    VERSION = "1"
    """Current version of serialization format.

    Need to be bumped when we change the YoutubeSnapshotSerializer.
    """

    serializer_class: type[AmberDataSerializer] = YoutubeSnapshotSerializer
