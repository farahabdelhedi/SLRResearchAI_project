
from unittest import result

from slrresearch.workflows.query_construction_workflow import (
    QueryConstructionWorkflow
)
from slrresearch.schemas.query_construction import (
    TechnologyExtractionResult
)


class FakeTechnologyAgent:
    def extract(self, questions):
        return TechnologyExtractionResult(
            technologies=["LLM", "Artificial Intelligence"],
            domain_concepts=["Education"],
            research_tasks=["Personalized Learning"]
        )


def test_query_construction_workflow():
    workflow = QueryConstructionWorkflow(
        technology_agent=FakeTechnologyAgent()
    )

    questions = [
        type("Question", (), {
            "identifier": "RQ1",
            "question": "How is AI used in education?"
        })()
    ]

    result = workflow.run(questions)

    assert result.technologies == [
        "LLM",
        "Artificial Intelligence"
    ]

    assert result.domain_concepts == ["Education"]

    assert result.research_tasks == ["Personalized Learning"]

    assert "LLM" in result.queries["openalex"]
    assert "LLM" in result.queries["crossref"]
    assert "LLM" in result.queries["semantic_scholar"]
    assert "Education" in result.queries["openalex"]
    assert "Personalized Learning" in result.queries["openalex"]

def test_workflow_without_questions():
    workflow = QueryConstructionWorkflow(
        technology_agent=FakeTechnologyAgent()
    )

    try:
        workflow.run([])
        assert False, "Une ValueError était attendue."
    except ValueError:
        assert True
