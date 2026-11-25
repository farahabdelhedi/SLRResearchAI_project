
from pydantic import BaseModel, Field


class TechnologyExtractionResult(BaseModel):
    """Concepts extraits des Research Questions."""

    technologies: list[str] = Field(default_factory=list)
    domain_concepts: list[str] = Field(default_factory=list)
    research_tasks: list[str] = Field(default_factory=list)


class QueryConstructionResult(BaseModel):
    """Résultat complet de la construction des requêtes."""

    technologies: list[str]
    domain_concepts: list[str]
    research_tasks: list[str]
    queries: dict[str, str]
