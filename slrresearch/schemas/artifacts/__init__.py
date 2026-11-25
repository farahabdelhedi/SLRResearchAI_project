"""Specialized, serializable artifacts for SLR workflow results."""

from slrresearch.schemas.artifacts.query_construction import (
    QueryConstructionArtifact,
)
from slrresearch.schemas.artifacts.research_questions import (
    ResearchQuestionsArtifact,
)
from slrresearch.schemas.artifacts.search_results import (
    SearchResultsArtifact,
)
from slrresearch.schemas.artifacts.technology_extraction import (
    TechnologyExtractionArtifact,
)

__all__ = [
    "QueryConstructionArtifact",
    "ResearchQuestionsArtifact",
    "SearchResultsArtifact",
    "TechnologyExtractionArtifact",
]
