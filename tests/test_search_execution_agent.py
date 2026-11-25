
from unittest.mock import Mock, patch

from slrresearch.agents.search_execution_agent import SearchExecutionAgent
from slrresearch.schemas.query_construction import QueryConstructionResult


def test_agent_initialization():
    model = Mock()

    agent = SearchExecutionAgent(model)

    assert agent.model is model
    assert agent.decision_policy.model is model

    assert set(agent.registry.names) == {
        "openalex",
        "crossref",
        "semantic_scholar",
    }


def test_agent_run_calls_react_engine():
    model = Mock()
    agent = SearchExecutionAgent(model)

    query_result = QueryConstructionResult(
        technologies=["Artificial Intelligence"],
        domain_concepts=["Education"],
        research_tasks=["Learning"],
        queries={
            "openalex": "AI education",
            "crossref": "artificial intelligence education",
            "semantic_scholar": "AI in learning",
        },
    )

    expected_result = Mock()

    with patch(
        "slrresearch.agents.search_execution_agent.run_react_agent",
        return_value=expected_result,
    ) as mock_engine:

        result = agent.run(
            objective="Find studies about AI in education",
            query_result=query_result,
            max_steps=4,
            target_papers=8,
        )

    assert result is expected_result

    mock_engine.assert_called_once()

    call_kwargs = mock_engine.call_args.kwargs

    assert call_kwargs["objective"] == "Find studies about AI in education"
    assert call_kwargs["queries"] == query_result.queries
    assert call_kwargs["max_steps"] == 4
    assert call_kwargs["target_papers"] == 8