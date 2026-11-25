"""Artifact model for extracted technologies and research concepts."""

from typing import Literal

from slrresearch.schemas.artifacts.base import ArtifactBase
from slrresearch.schemas.query_construction import TechnologyExtractionResult


class TechnologyExtractionArtifact(ArtifactBase):
    """Persistable result of technology and concept extraction."""

    artifact_type: Literal["technology_extraction"] = "technology_extraction"
    result: TechnologyExtractionResult
