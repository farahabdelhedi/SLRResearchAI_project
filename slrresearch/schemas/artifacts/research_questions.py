"""Artifact model for generated and validated research questions."""

from typing import Literal

from slrresearch.schemas.artifacts.base import ArtifactBase
from slrresearch.schemas.research_question import WorkflowOutcome


class ResearchQuestionsArtifact(ArtifactBase):
    """Persistable result of the research-question agent."""

    artifact_type: Literal["research_questions"] = "research_questions"
    result: WorkflowOutcome
