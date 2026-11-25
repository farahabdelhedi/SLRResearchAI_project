
"""
Workflow de validation humaine des Research Questions.

Ce module permet au chercheur de :
- Recevoir les questions générées par l'IA.
- Saisir ses propres questions.
- Modifier les questions.
- Bénéficier d'une réparation automatique en cas d'erreur.
- Approuver ou rejeter les questions.
"""

from dataclasses import dataclass
from typing import Literal

from slrresearch.schemas.research_question import (
    ResearchQuestion,
    WorkflowOutcome,
)

from slrresearch.validators.research_question_validator import (
    validate_free_text,
    validate_questions,
)

from slrresearch.agents.research_question_agent import (
    ResearchQuestionAgent,
)


HumanApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
]


@dataclass
class HumanReview:
    """Représente une session de validation humaine."""

    original_questions: list[ResearchQuestion]
    questions: list[ResearchQuestion]
    status: HumanApprovalStatus = "pending"
    rejection_reason: str | None = None


class ResearchQuestionWorkflow:
    """Gère le processus de validation humaine des questions."""

    def __init__(self, agent: ResearchQuestionAgent):
        self.agent = agent

    @staticmethod
    def start_review(
        outcome: WorkflowOutcome,
    ) -> HumanReview:
        """Démarre une validation humaine après validation automatique."""

        if outcome.status not in {"accepted", "repaired"}:
            raise ValueError(
                "Les questions doivent d'abord réussir "
                "la validation automatique."
            )

        if len(outcome.questions) != 3:
            raise ValueError(
                "Trois questions sont nécessaires "
                "pour démarrer la validation humaine."
            )

        questions = list(outcome.questions)

        return HumanReview(
            original_questions=list(questions),
            questions=list(questions),
        )

    def edit_questions(
        self,
        review: HumanReview,
        edited_text: str,
    ) -> HumanReview:
        """
        Modifie les questions.

        Processus :
        1. Première validation.
        2. Une seule tentative de réparation par le LLM si nécessaire.
        3. Deuxième validation obligatoire.
        4. Enregistrement uniquement si le résultat est valide.
        """

        if review.status != "pending":
            raise ValueError(
                "La modification est impossible : "
                "la validation humaine est déjà terminée."
            )

        # Première validation
        try:
            records = validate_free_text(edited_text)
            validated_questions = validate_questions(records)

        except (ValueError, TypeError) as first_error:

            # Une seule tentative de réparation
            try:
                repaired_response = self.agent.repair(
                    text=edited_text,
                    error=str(first_error),
                )

                repaired_text = repaired_response.content

            except Exception as repair_error:
                raise ValueError(
                    "La réparation automatique a échoué : "
                    f"{str(repair_error)}"
                ) from repair_error

            # Revalidation obligatoire
            try:
                repaired_records = validate_free_text(repaired_text)
                validated_questions = validate_questions(repaired_records)

            except (ValueError, TypeError) as second_error:
                raise ValueError(
                    "Les questions restent invalides après "
                    "une tentative de réparation automatique. "
                    f"Erreur : {str(second_error)}"
                ) from second_error

        # Enregistrer uniquement les questions validées
        review.questions = validated_questions

        return review

    @staticmethod
    def approve(review: HumanReview) -> HumanReview:
        """Enregistre l'approbation du chercheur."""

        if review.status != "pending":
            raise ValueError(
                "Cette session de validation est déjà terminée."
            )

        text = ResearchQuestionWorkflow.format_questions(
            review.questions
        )

        records = validate_free_text(text)
        review.questions = validate_questions(records)

        review.status = "approved"
        review.rejection_reason = None

        return review

    @staticmethod
    def reject(
        review: HumanReview,
        reason: str = "",
    ) -> HumanReview:
        """Enregistre le refus du chercheur."""

        if review.status != "pending":
            raise ValueError(
                "Cette session de validation est déjà terminée."
            )

        review.status = "rejected"
        review.rejection_reason = reason.strip() or None

        return review

    @staticmethod
    def get_approved_questions(
        review: HumanReview,
    ) -> list[ResearchQuestion]:
        """Retourne les questions uniquement après approbation."""

        if review.status != "approved":
            raise ValueError(
                "Les questions doivent être approuvées par l'humain."
            )

        return list(review.questions)

    @staticmethod
    def format_questions(
        questions: list[ResearchQuestion],
    ) -> str:
        """Transforme les questions en texte au format RQ1, RQ2, RQ3."""

        return "\n".join(
            f"{question.identifier}. {question.question}"
            for question in questions
        )
