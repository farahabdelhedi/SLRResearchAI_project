
from dataclasses import dataclass
from typing import Literal

from slrresearch.schemas.screening import ScreeningCriteria


CriteriaApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
]


@dataclass
class CriteriaReview:
    """Représente une session de validation humaine des critères."""

    original_criteria: ScreeningCriteria
    criteria: ScreeningCriteria
    status: CriteriaApprovalStatus = "pending"
    rejection_reason: str | None = None


class CriteriaGenerationWorkflow:
    """Gère le processus de validation humaine des critères de screening."""

    @staticmethod
    def start_review(
        criteria: ScreeningCriteria,
    ) -> CriteriaReview:
        """Démarre la validation humaine des critères générés."""

        validated_criteria = ScreeningCriteria.model_validate(
            criteria.model_dump()
        )

        return CriteriaReview(
            original_criteria=validated_criteria.model_copy(deep=True),
            criteria=validated_criteria.model_copy(deep=True),
        )

    @staticmethod
    def edit_criteria(
        review: CriteriaReview,
        inclusion_criteria: list[str],
        exclusion_criteria: list[str],
        inclusion_terms: list[str] | None = None,
        exclusion_terms: list[str] | None = None,
    ) -> CriteriaReview:
        """Permet au chercheur de modifier les critères et les termes lexicaux."""

        if review.status != "pending":
            raise ValueError(
                "La modification est impossible : "
                "la validation humaine est déjà terminée."
            )

        edited_data = {
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "inclusion_terms": (
                inclusion_terms
                if inclusion_terms is not None
                else review.criteria.inclusion_terms
            ),
            "exclusion_terms": (
                exclusion_terms
                if exclusion_terms is not None
                else review.criteria.exclusion_terms
            ),
        }

        review.criteria = ScreeningCriteria.model_validate(edited_data)

        return review

    @staticmethod
    def approve(review: CriteriaReview) -> CriteriaReview:
        """Enregistre l'approbation du chercheur."""

        if review.status != "pending":
            raise ValueError(
                "Cette session de validation est déjà terminée."
            )

        review.criteria = ScreeningCriteria.model_validate(
            review.criteria.model_dump()
        )

        review.status = "approved"
        review.rejection_reason = None

        return review

    @staticmethod
    def reject(
        review: CriteriaReview,
        reason: str = "",
    ) -> CriteriaReview:
        """Enregistre le refus du chercheur."""

        if review.status != "pending":
            raise ValueError(
                "Cette session de validation est déjà terminée."
            )

        review.status = "rejected"
        review.rejection_reason = reason.strip() or None

        return review

    @staticmethod
    def get_approved_criteria(
        review: CriteriaReview,
    ) -> ScreeningCriteria:
        """Retourne les critères uniquement après approbation."""

        if review.status != "approved":
            raise ValueError(
                "Les critères doivent être approuvés par le chercheur."
            )

        return review.criteria.model_copy(deep=True)
