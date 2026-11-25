
from types import SimpleNamespace

import pytest

from slrresearch.schemas.research_question import WorkflowOutcome
from slrresearch.validators.research_question_validator import (
    validate_free_text,
    validate_questions,
)
from slrresearch.workflows.research_question_workflow import (
    ResearchQuestionWorkflow,
)


class FakeResearchQuestionAgent:
    """Simule le comportement de ResearchQuestionAgent sans Ollama."""

    def __init__(self, repaired_text=None):
        self.repaired_text = repaired_text
        self.repair_called = False

    def repair(self, text: str, error: str):
        self.repair_called = True

        return SimpleNamespace(content=self.repaired_text)


def make_workflow(repaired_text=None):
    """Crée un workflow avec un faux agent."""
    agent = FakeResearchQuestionAgent(repaired_text=repaired_text)
    workflow = ResearchQuestionWorkflow(agent=agent)

    return workflow, agent


def make_outcome():
    """Prépare un résultat dont les trois questions sont déjà valides."""
    text = (
        "RQ1. Comment les LLM peuvent-ils automatiser le screening "
        "des titres et résumés ?\n"
        "RQ2. Quelles sont les performances des LLM dans le screening "
        "des articles scientifiques ?\n"
        "RQ3. Quels facteurs influencent la fiabilité des LLM "
        "dans le processus de screening ?"
    )

    records = validate_free_text(text)
    questions = validate_questions(records)

    return WorkflowOutcome(
        status="accepted",
        text=text,
        questions=questions,
    )


def test_human_approves_without_modification():
    """L'humain accepte directement les questions."""
    workflow, agent = make_workflow()

    review = workflow.start_review(make_outcome())

    assert review.status == "pending"

    original_questions = list(review.questions)

    workflow.approve(review)

    assert review.status == "approved"
    assert review.questions == original_questions
    assert agent.repair_called is False


def test_human_edits_then_approves():
    """L'humain modifie des questions valides puis les accepte."""
    workflow, agent = make_workflow()

    review = workflow.start_review(make_outcome())

    edited_text = (
        "RQ1. Comment les LLM améliorent-ils le screening "
        "des titres et résumés ?\n"
        "RQ2. Comment comparer les performances des LLM "
        "avec celles des méthodes traditionnelles ?\n"
        "RQ3. Quels facteurs influencent la précision des LLM "
        "dans le screening des articles ?"
    )

    workflow.edit_questions(review, edited_text)
    workflow.approve(review)

    assert review.status == "approved"
    assert "améliorent-ils" in review.questions[0].question
    assert agent.repair_called is False


def test_human_rejects_questions():
    """L'humain rejette les questions générées."""
    workflow, agent = make_workflow()

    review = workflow.start_review(make_outcome())

    workflow.reject(
        review,
        "Les questions ne correspondent pas à mon objectif.",
    )

    assert review.status == "rejected"
    assert review.rejection_reason == (
        "Les questions ne correspondent pas à mon objectif."
    )
    assert agent.repair_called is False


def test_invalid_human_edit_is_repaired():
    """Le LLM répare les questions invalides puis elles sont revalidées."""

    repaired_text = (
        "RQ1. Comment les LLM automatisent-ils le screening "
        "des titres et résumés ?\n"
        "RQ2. Quelles sont les performances des LLM "
        "dans le screening scientifique ?\n"
        "RQ3. Quels facteurs influencent la fiabilité des LLM "
        "dans le screening des articles ?"
    )

    workflow, agent = make_workflow(repaired_text)

    review = workflow.start_review(make_outcome())

    invalid_text = (
        "RQ1. Comment les LLM automatisent-ils le screening ?\n"
        "R2. Question avec un identifiant incorrect\n"
        "RQ3. Quels facteurs influencent la fiabilité des LLM ?"
    )

    workflow.edit_questions(review, invalid_text)

    assert agent.repair_called is True
    assert review.status == "pending"
    assert len(review.questions) == 3
    assert review.questions[0].question == (
        "Comment les LLM automatisent-ils le screening "
        "des titres et résumés ?"
    )


def test_failed_repair_preserves_previous_questions():
    """Si la réparation échoue, les anciennes questions sont conservées."""

    workflow, agent = make_workflow(
        repaired_text="Texte toujours invalide."
    )

    review = workflow.start_review(make_outcome())
    original_questions = list(review.questions)

    invalid_text = (
        "RQ1. Question incorrecte\n"
        "R2. Identifiant incorrect\n"
        "RQ3. Question incorrecte"
    )

    with pytest.raises(ValueError):
        workflow.edit_questions(review, invalid_text)

    assert agent.repair_called is True
    assert review.questions == original_questions
    assert review.status == "pending"
