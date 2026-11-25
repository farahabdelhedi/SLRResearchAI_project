"""Artifact model for generated bibliographic search queries."""

from typing import Literal

from slrresearch.schemas.artifacts.base import ArtifactBase
from slrresearch.schemas.query_construction import QueryConstructionResult


class QueryConstructionArtifact(ArtifactBase):
    """Persistable result of the query-construction workflow."""

    artifact_type: Literal["query_construction"] = "query_construction"
    result: QueryConstructionResult
