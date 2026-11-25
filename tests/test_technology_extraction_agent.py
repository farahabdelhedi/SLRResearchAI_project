
import pytest

from slrresearch.agents.technology_extraction_agent import (
    TechnologyExtractionAgent
)


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeModel:
    def invoke(self, prompt):
        return FakeResponse("""
        {
            "technologies": [
                "LLM",
                "Artificial Intelligence",
                "LLM"
            ],
            "domain_concepts": [
                "Education",
                "Higher Education"
            ],
            "research_tasks": [
                "Personalized Learning",
                "Personalized Learning"
            ]
        }
        """)


def test_extract_three_categories_and_remove_duplicates():
    agent = TechnologyExtractionAgent(model=FakeModel())

    result = agent.extract([
        type("Question", (), {
            "identifier": "RQ1",
            "question": "How is AI used in education?"
        })()
    ])

    assert result.technologies == [
        "LLM",
        "Artificial Intelligence"
    ]

    assert result.domain_concepts == [
        "Education",
        "Higher Education"
    ]

    assert result.research_tasks == [
        "Personalized Learning"
    ]


def test_extract_with_empty_category():
    class EmptyCategoryModel:
        def invoke(self, prompt):
            return FakeResponse("""
            {
                "technologies": [],
                "domain_concepts": ["Healthcare"],
                "research_tasks": ["Disease Detection"]
            }
            """)

    agent = TechnologyExtractionAgent(model=EmptyCategoryModel())

    result = agent.extract([
        type("Question", (), {
            "identifier": "RQ1",
            "question": "How is disease detection performed?"
        })()
    ])

    assert result.technologies == []
    assert result.domain_concepts == ["Healthcare"]
    assert result.research_tasks == ["Disease Detection"]


def test_extract_without_questions():
    agent = TechnologyExtractionAgent(model=FakeModel())

    with pytest.raises(ValueError):
        agent.extract([])
