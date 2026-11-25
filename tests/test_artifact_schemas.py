import json
from datetime import datetime, timezone

from pydantic import ValidationError
import pytest

from slrresearch.core.react.contracts import SearchState
from slrresearch.schemas.artifacts import (
    QueryConstructionArtifact,
    ResearchQuestionsArtifact,
    SearchResultsArtifact,
    TechnologyExtractionArtifact,
)
from slrresearch.schemas.query_construction import (
    QueryConstructionResult,
    TechnologyExtractionResult,
)
from slrresearch.schemas.research_question import (
    ResearchQuestion,
    WorkflowOutcome,
)


def test_research_questions_artifact_reuses_workflow_outcome():
    result = WorkflowOutcome(
        status="accepted",
        text=(
            "RQ1. Comment les LLM améliorent-ils le screening ?\n"
            "RQ2. Quel contrôle humain doit-il être conservé ?\n"
            "RQ3. Quelles métriques évaluent cette amélioration ?"
        ),
        questions=[
            ResearchQuestion(
                identifier="RQ1",
                question="Comment les LLM améliorent-ils le screening ?",
            ),
            ResearchQuestion(
                identifier="RQ2",
                question="Quel contrôle humain doit-il être conservé ?",
            ),
            ResearchQuestion(
                identifier="RQ3",
                question="Quelles métriques évaluent cette amélioration ?",
            ),
        ],
    )

    artifact = ResearchQuestionsArtifact(
        project_id="project-001",
        result=result,
    )

    serialized = artifact.model_dump(mode="json")

    assert artifact.artifact_type == "research_questions"
    assert isinstance(artifact.result, WorkflowOutcome)
    assert serialized["result"]["questions"][0]["identifier"] == "RQ1"
    assert json.loads(artifact.model_dump_json())["project_id"] == "project-001"


def test_technology_extraction_artifact_reuses_result_schema():
    artifact = TechnologyExtractionArtifact(
        project_id="project-001",
        depends_on=["rq-001"],
        result=TechnologyExtractionResult(
            technologies=["LLM"],
            domain_concepts=["systematic literature review"],
            research_tasks=["title and abstract screening"],
        ),
    )

    assert artifact.artifact_type == "technology_extraction"
    assert artifact.depends_on == ["rq-001"]
    assert artifact.model_dump(mode="json")["result"]["technologies"] == [
        "LLM"
    ]


def test_query_construction_artifact_reuses_result_schema():
    artifact = QueryConstructionArtifact(
        project_id="project-001",
        depends_on=["rq-001"],
        result=QueryConstructionResult(
            technologies=["LLM"],
            domain_concepts=["systematic literature review"],
            research_tasks=["screening"],
            queries={"openalex": "LLM AND screening"},
        ),
    )

    assert artifact.artifact_type == "query_construction"
    assert isinstance(artifact.result, QueryConstructionResult)
    assert artifact.model_dump(mode="json")["result"]["queries"] == {
        "openalex": "LLM AND screening"
    }


def test_search_results_artifact_serializes_search_state():
    artifact = SearchResultsArtifact(
        project_id="project-001",
        depends_on=["query-001"],
        result=SearchState(
            objective="Find research about LLM-assisted screening",
            queries={"openalex": "LLM AND screening"},
            papers=[
                {
                    "id": "paper-001",
                    "title": "LLMs for SLR screening",
                    "source": "openalex",
                }
            ],
        ),
    )

    serialized = artifact.model_dump(mode="json")

    assert artifact.artifact_type == "search_results"
    assert isinstance(artifact.result, SearchState)
    assert serialized["result"]["papers"][0]["source"] == "openalex"
    assert serialized["result"]["observations"] == []


def test_artifact_metadata_defaults_are_serializable():
    artifact = TechnologyExtractionArtifact(
        project_id="project-001",
        result=TechnologyExtractionResult(technologies=["LLM"]),
    )

    serialized = artifact.model_dump(mode="json")

    assert serialized["artifact_id"]
    assert serialized["schema_version"] == "1.0"
    assert serialized["depends_on"] == []
    created_at = datetime.fromisoformat(
        serialized["created_at"].replace("Z", "+00:00")
    )
    assert created_at.utcoffset() == timezone.utc.utcoffset(created_at)


def test_artifact_type_is_fixed_by_specialized_model():
    with pytest.raises(ValidationError):
        TechnologyExtractionArtifact(
            project_id="project-001",
            artifact_type="research_questions",
            result=TechnologyExtractionResult(technologies=["LLM"]),
        )
