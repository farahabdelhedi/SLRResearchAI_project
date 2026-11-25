"""Artifact model for literature-search execution results."""

from typing import Literal

from slrresearch.core.react.contracts import SearchState
from slrresearch.schemas.artifacts.base import ArtifactBase


class SearchResultsArtifact(ArtifactBase):
    """Persistable result, papers, and execution trace of a search."""

    artifact_type: Literal["search_results"] = "search_results"
    result: SearchState
