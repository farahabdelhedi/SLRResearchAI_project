
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from slrresearch.core.react.contracts import PaperRecord


# =========================
# 1. DEDUPLICATION
# =========================

class DuplicateGroup(BaseModel):
    """Groupe d'articles considérés comme des doublons."""

    canonical_paper_id: str
    duplicate_paper_ids: list[str]
    match_type: Literal["doi", "identifier", "title"]


class DeduplicationResult(BaseModel):
    """Résultat de la déduplication."""

    unique_papers: list[PaperRecord]
    duplicate_groups: list[DuplicateGroup] = Field(default_factory=list)
    total_input: int = 0
    total_unique: int = 0


# =========================
# 2. TITLE / ABSTRACT SCREENING
# =========================

class ScreeningIndicators(BaseModel):
    """Indicateurs utilisés par le screening déterministe."""

    inclusion_matches: list[str] = Field(default_factory=list)
    exclusion_matches: list[str] = Field(default_factory=list)
    information_sufficient: bool
    conflict: bool


class ScreeningDecision(BaseModel):
    """Décision du screening déterministe."""

    paper_id: str
    decision: Literal["include", "exclude", "uncertain"]
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)
    indicators: ScreeningIndicators
    needs_human_review: bool = False

class CriterionAssessment(BaseModel):
    """Évaluation d'un critère pour un article."""

    criterion: str
    status: Literal[
        "satisfied",
        "not_satisfied",
        "uncertain",
    ]
    evidence: str = ""
    explanation: str = ""
class LLMScreeningDecision(BaseModel):
    """Décision du LLM avec une preuve extraite de l'article."""

    paper_id: str
    decision: Literal["include", "exclude", "uncertain"]
    criterion_assessments: list[CriterionAssessment] = Field(
    default_factory=list
    )
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = Field(min_length=1)
    evidence: str = ""
    needs_human_review: bool = False

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value):
        if isinstance(value, (int, float)) and 1 < value <= 100:
            return value / 100
        return value
class CriterionSimilarity(BaseModel):
    """Similarité entre un article et un critère."""

    criterion: str
    similarity: float = Field(ge=-1, le=1)


class SemanticScreeningResult(BaseModel):
    """Résultat du screening sémantique d'un article."""

    paper_id: str
    inclusion_scores: list[CriterionSimilarity] = Field(
        default_factory=list
    )
    exclusion_scores: list[CriterionSimilarity] = Field(
        default_factory=list
    )


class ComparisonResult(BaseModel):
    """Résultat de la comparaison des trois analyses."""

    paper_id: str

    # Résultat du screening déterministe
    deterministic_decision: ScreeningDecision

    # Résultat du screening sémantique
    semantic_result: SemanticScreeningResult

    # Résultat de l'analyse par LLM
    llm_decision: LLMScreeningDecision

    # Décision finale de la fusion
    final_decision: Literal[
        "include",
        "exclude",
        "uncertain",
    ]

    agreement: bool
    needs_human_review: bool = False
    escalation_reason: str | None = None


# =========================
# 3. PDF RETRIEVAL
# =========================

class PDFRetrievalResult(BaseModel):
    """Résultat de la récupération du PDF."""

    paper_id: str
    status: Literal[
        "found",
        "not_found",
        "download_error",
        "invalid_pdf",
    ]
    pdf_url: str = ""
    local_path: str | None = None
    error: str | None = None


# =========================
# 4. FULL-TEXT ELIGIBILITY
# =========================

class FullTextEligibilityDecision(BaseModel):
    """Décision finale basée sur le texte intégral."""

    paper_id: str
    decision: Literal["include", "exclude", "uncertain"]
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    needs_human_review: bool = False


# =========================
# 5. SCREENING RESULT
# =========================

class ScreeningResult(BaseModel):
    """Résultat global du Screening Agent."""

    deduplication: DeduplicationResult
    title_abstract_decisions: list[ComparisonResult] = Field(
        default_factory=list
    )
    human_review_queue: list[str] = Field(default_factory=list)
    pdf_results: list[PDFRetrievalResult] = Field(default_factory=list)
    full_text_decisions: list[FullTextEligibilityDecision] = Field(
        default_factory=list
    )
    selected_papers: list[PaperRecord] = Field(default_factory=list)

class ScreeningCriteria(BaseModel):
    inclusion_criteria: list[str] = Field(min_length=1)
    exclusion_criteria: list[str] = Field(min_length=1)

    inclusion_terms: list[str] = Field(default_factory=list)
    exclusion_terms: list[str] = Field(default_factory=list)
