"""Shared metadata for specialized SLR artifacts."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class ArtifactBase(BaseModel):
    """Common identity, versioning, and provenance for an artifact."""

    artifact_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    project_id: str
    artifact_type: str
    schema_version: str = "1.0"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    depends_on: list[str] = Field(default_factory=list)
