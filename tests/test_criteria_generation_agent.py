
import pytest
from pydantic import ValidationError
from types import SimpleNamespace

from slrresearch.agents.criteria_generation_agent import (
    CriteriaGenerationAgent,
)
from slrresearch.schemas.screening import ScreeningCriteria


class FakeModel:
    """Faux modèle qui retourne une réponse prédéfinie."""

    def __init__(self, content):
        self.content = content
        self.received_messages = None

    def invoke(self, messages):
        self.received_messages = messages

        return SimpleNamespace(
            content=self.content,
            usage_metadata={},
            response_metadata={},
        )


@pytest.fixture
def valid_json_response():
    return """
    {
        "inclusion_criteria": [
            "Studies applying machine learning in healthcare.",
            "Studies addressing medical diagnosis."
        ],
        "exclusion_criteria": [
            "Studies unrelated to healthcare."
        ]
    }
    """


@pytest.fixture
def approved_questions():
    return [
        "RQ1: How is machine learning applied in healthcare?",
        "RQ2: What are the challenges of these applications?"
    ]


def test_generate_returns_screening_criteria(
    valid_json_response,
    approved_questions,
):
    model = FakeModel(valid_json_response)
    agent = CriteriaGenerationAgent(model=model)

    result = agent.generate(
        objective="Study machine learning applications in healthcare.",
        approved_questions=approved_questions,
    )

    assert isinstance(result, ScreeningCriteria)
    assert len(result.inclusion_criteria) == 2
    assert len(result.exclusion_criteria) == 1


def test_generate_calls_model(
    valid_json_response,
    approved_questions,
):
    model = FakeModel(valid_json_response)
    agent = CriteriaGenerationAgent(model=model)

    agent.generate(
        objective="Study machine learning applications in healthcare.",
        approved_questions=approved_questions,
    )

    assert model.received_messages is not None
    assert "machine learning" in model.received_messages.lower()


def test_generate_rejects_invalid_json(approved_questions):
    model = FakeModel("This is not a valid JSON response.")
    agent = CriteriaGenerationAgent(model=model)

    with pytest.raises(ValueError, match="JSON valide"):
        agent.generate(
            objective="Study machine learning applications in healthcare.",
            approved_questions=approved_questions,
        )


def test_generate_rejects_invalid_criteria(approved_questions):
    invalid_response = """
    {
        "inclusion_criteria": [],
        "exclusion_criteria": [
            "Studies unrelated to healthcare."
        ]
    }
    """

    model = FakeModel(invalid_response)
    agent = CriteriaGenerationAgent(model=model)

    with pytest.raises(ValidationError):
        agent.generate(
            objective="Study machine learning applications in healthcare.",
            approved_questions=approved_questions,
        )


def test_generate_rejects_empty_objective(approved_questions):
    model = FakeModel("{}")
    agent = CriteriaGenerationAgent(model=model)

    with pytest.raises(ValueError, match="objectif"):
        agent.generate(
            objective="",
            approved_questions=approved_questions,
        )


def test_generate_rejects_empty_questions():
    model = FakeModel("{}")
    agent = CriteriaGenerationAgent(model=model)

    with pytest.raises(ValueError, match="Research Question"):
        agent.generate(
            objective="Study machine learning applications in healthcare.",
            approved_questions=[],
        )


def test_generate_uses_configured_provider(valid_json_response, approved_questions):
    model = FakeModel(valid_json_response)
    agent = CriteriaGenerationAgent(
        model=model,
        provider="ollama",
    )

    agent.generate(
        objective="Study machine learning applications in healthcare.",
        approved_questions=approved_questions,
    )

    # Le provider est transmis au service centralisé.
    # Le test vérifie ici que l'agent accepte sa configuration.
    assert agent.provider == "ollama"


def test_generate_uses_default_provider(valid_json_response, approved_questions):
    model = FakeModel(valid_json_response)
    agent = CriteriaGenerationAgent(model=model)

    agent.generate(
        objective="Study machine learning applications in healthcare.",
        approved_questions=approved_questions,
    )

    assert agent.provider == "demo"
