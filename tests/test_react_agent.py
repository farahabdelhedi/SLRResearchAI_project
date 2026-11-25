
from slrresearch.core.react.engine import run_react_agent
from slrresearch.core.react.policies import ScriptedPolicy
from slrresearch.services.search.tools import SearchTool, ToolRegistry


def create_registry(search_function):
    return ToolRegistry([
        SearchTool(name="openalex", search=search_function),
        SearchTool(name="crossref", search=search_function),
        SearchTool(name="semantic_scholar", search=search_function),
    ])


def test_search_uses_validated_query():
    """Le moteur injecte la requête validée sans la demander au LLM."""

    received_queries = []

    def fake_search(query, limit):
        received_queries.append(query)
        return [
            {
                "id": "paper-1",
                "title": "Artificial Intelligence in Education",
                "abstract": "An example paper.",
                "doi": "10.1234/example",
                "url": "https://example.com",
                "open_access": True,
            }
        ]

    queries = {
        "openalex": '"LLM" AND "Education"',
        "crossref": '"LLM" AND "Education"',
        "semantic_scholar": '"LLM" AND "Education"',
    }

    policy = ScriptedPolicy([
        {
            "action": "search",
            "tool": "openalex",
            "limit": 10,
        }
    ])

    state = run_react_agent(
        objective="Étudier l'utilisation des LLM dans l'éducation",
        queries=queries,
        registry=create_registry(fake_search),
        decide=policy,
        max_steps=5,
        target_papers=1,
    )

    assert received_queries == ['"LLM" AND "Education"']
    assert state.papers
    assert state.actions_executed[0].query == '"LLM" AND "Education"'
    assert state.stop_reason == "target_reached"


def test_agent_can_finish():
    """L'agent peut terminer sans lancer de recherche."""

    policy = ScriptedPolicy([
        {"action": "finish"}
    ])

    def fake_search(query, limit):
        return []

    state = run_react_agent(
        objective="Recherche scientifique",
        queries={"openalex": "LLM"},
        registry=create_registry(fake_search),
        decide=policy,
    )

    assert state.finished is True
    assert state.stop_reason == "agent_finish"
    assert len(state.papers) == 0
    assert len(state.actions_executed) == 1


def test_missing_query_becomes_invalid_action():
    """Une source sans requête validée produit une observation invalide."""

    policy = ScriptedPolicy([
        {
            "action": "search",
            "tool": "openalex",
            "limit": 10,
        },
        {"action": "finish"},
    ])

    def fake_search(query, limit):
        return []

    state = run_react_agent(
        objective="Recherche scientifique",
        queries={},
        registry=create_registry(fake_search),
        decide=policy,
    )

    assert state.observations[0].status == "invalid_action"
    assert "Aucune requête validée" in state.observations[0].error
    assert state.stop_reason == "agent_finish"


def test_agent_stops_at_max_steps():
    """Le moteur respecte le nombre maximal de tours."""

    policy = ScriptedPolicy([
        {
            "action": "search",
            "tool": "openalex",
            "limit": 10,
        },
        {
            "action": "search",
            "tool": "crossref",
            "limit": 10,
        },
    ])

    def fake_search(query, limit):
        return []

    state = run_react_agent(
        objective="Recherche scientifique",
        queries={
            "openalex": "LLM Education",
            "crossref": "LLM Education",
        },
        registry=create_registry(fake_search),
        decide=policy,
        max_steps=1,
        target_papers=100,
    )

    assert state.finished is True
    assert state.stop_reason == "max_steps"
    assert state.step == 1
    assert len(state.actions_executed) == 1
