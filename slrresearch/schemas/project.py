
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    Représente un projet de Systematic Literature Review.
    """

    project_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    topic: str
    objective: str
    context: str = ""

    status: str = "created"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
