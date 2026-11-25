from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class PaperRecord(BaseModel):
    """Article normalisé, indépendant de l'API qui l'a produit."""

    id: str
    title: str
    abstract: str = ""
    doi: str = ""
    source: str
    url: str = ""
    open_access: bool = False



class AgentAction(BaseModel):
    """Décision structurée du LLM ou action préparée par le moteur."""

    action: Literal["search", "finish"]
    tool: str | None = None
    query: str | None = None
    limit: int | None = Field(default=None, ge=1, le=20)

    @model_validator(mode="after")
    def validate_action_arguments(self):
        if self.action == "search":
            if not self.tool:
                raise ValueError("search exige un outil")

            if self.limit is None:
                raise ValueError("search exige une limite")

            # La requête peut être absente dans la décision initiale.
            # Elle sera ajoutée par le moteur avant l'exécution.

        else:
            if (
                self.tool is not None
                or self.query is not None
                or self.limit is not None
            ):
                raise ValueError(
                    "finish ne doit contenir aucun argument d'outil"
                )

        return self


class Observation(BaseModel):
    """Retour structuré ajouté à l'état après une action."""

    tool: str | None = None
    status: Literal[
        "success",
        "empty",
        "rate_limited",
        "http_error",
        "network_error",
        "unauthorized",
        "invalid_action",
    ]
    count: int = 0
    latency_seconds: float = 0.0
    error: str | None = None
    papers: list[PaperRecord] = Field(default_factory=list)
    raw_action: dict[str, Any] | None = None


class TraceEvent(BaseModel):
    step: int
    action: dict[str, Any]
    observation: Observation

#c'est le cerveau /memoire de l'execution 
class SearchState(BaseModel):
    """État détenu par le runtime entre deux décisions."""

    objective: str
    queries: dict[str, str]
    papers: list[PaperRecord] = Field(default_factory=list)
    actions_executed: list[AgentAction] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    step: int = 0
    finished: bool = False
    stop_reason: str | None = None

