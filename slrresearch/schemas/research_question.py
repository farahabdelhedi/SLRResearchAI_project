
"""
Schémas de données du ResearchQuestionAgent.

Ce module centralise les structures utilisées pour :
- stocker les questions générées par le LLM ;
- représenter une Research Question validée ;
- représenter le résultat du workflow de validation.
"""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


@dataclass
class FreeTextQuestions:
    """
    Résultat brut de la génération des Research Questions.

    Acquis du TD01 : conserve le texte généré et les métadonnées
    observables de l'appel au modèle.
    """

    text: str
    provider: str
    latency_seconds: float
    system_prompt: str
    user_prompt: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None


class ResearchQuestion(BaseModel):
    """
    Contrat d'une Research Question après validation.

    Acquis du TD02 : garantit un identifiant conforme
    et une formulation suffisamment longue.
    """

    identifier: str = Field(
        pattern=r"^RQ[0-9]+$",
        description="Identifiant de la question, par exemple RQ1."
    )

    question: str = Field(
        min_length=15,
        description="Formulation textuelle de la question de recherche."
    )


class WorkflowOutcome(BaseModel):
    """
    Résultat du workflow de génération et de validation.

    Permet de distinguer :
    - accepted : questions initialement conformes ;
    - repaired : questions conformes après réparation ;
    - human_required : intervention humaine nécessaire.
    """

    status: Literal["accepted", "repaired", "human_required"]

    text: str = Field(
        description="Texte final des questions de recherche."
    )

    questions: list[ResearchQuestion] = Field(
        default_factory=list,
        description="Questions validées selon le contrat Pydantic."
    )

    error: str | None = Field(
        default=None,
        description="Erreur rencontrée si une intervention humaine est nécessaire."
    )

    repair_attempts: int = Field(
        default=0,
        ge=0,
        description="Nombre de tentatives de réparation effectuées."
    )
