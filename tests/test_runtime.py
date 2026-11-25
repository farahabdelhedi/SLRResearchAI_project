
import httpx

from slrresearch.core.react.contracts import (
    AgentAction,
    Observation,
    PaperRecord,
    SearchState,
)
from slrresearch.core.react.runtime import (
    execute_authorized_action,
    update_state,
)
from slrresearch.services.search.tools import (
    SearchTool,
    ToolRegistry,
)


def create_registry(search_function):
    return ToolRegistry([
        SearchTool(name="openalex", search=search_function)
    ])


def create_action():
    return AgentAction(
        action="search",
        tool="openalex",
        query="LLM Education",
        limit=5,
    )


def test_execute_authorized_search():
    """Vérifier l'exécution normale d'une recherche."""

    def fake_search(query, limit):
        assert query == "LLM Education"
        assert limit == 5

        return [{
            "id": "paper-1",
            "title": "LLM in Education",
            "doi": "10.1234/example",
        }]

    observation = execute_authorized_action(
        create_action(),
        create_registry(fake_search),
    )

    assert observation.status == "success"
    assert observation.count == 1
    assert observation.papers[0].source == "openalex"


def test_unauthorized_tool():
    """Une source absente de la liste blanche est refusée."""

    registry = create_registry(lambda query, limit: [])

    action = AgentAction(
        action="search",
        tool="unknown_source",
        query="LLM",
        limit=5,
    )

    observation = execute_authorized_action(action, registry)

    assert observation.status == "unauthorized"
    assert observation.error is not None


def test_empty_search_result():
    """Une recherche sans résultat produit une observation empty."""

    observation = execute_authorized_action(
        create_action(),
        create_registry(lambda query, limit: []),
    )

    assert observation.status == "empty"
    assert observation.count == 0
    assert observation.papers == []


def test_http_error():
    """Une erreur HTTP est correctement convertie."""

    def failing_search(query, limit):
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError(
            "Server error",
            request=request,
            response=response,
        )

    observation = execute_authorized_action(
        create_action(),
        create_registry(failing_search),
    )

    assert observation.status == "http_error"
    assert observation.error == "HTTP 500"


def test_rate_limit_error():
    """Une erreur HTTP 429 est reconnue comme rate_limited."""

    def failing_search(query, limit):
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(429, request=request)
        raise httpx.HTTPStatusError(
            "Too many requests",
            request=request,
            response=response,
        )

    observation = execute_authorized_action(
        create_action(),
        create_registry(failing_search),
    )

    assert observation.status == "rate_limited"


def test_network_error():
    """Une erreur réseau est correctement convertie."""

    def failing_search(query, limit):
        raise httpx.ConnectError("Connection failed")

    observation = execute_authorized_action(
        create_action(),
        create_registry(failing_search),
    )

    assert observation.status == "network_error"


def test_deduplicate_papers():
    """Les articles avec le même DOI ne sont enregistrés qu'une fois."""

    state = SearchState(
        objective="Research",
        queries={},
    )

    paper1 = PaperRecord(
        id="1",
        title="LLM in Education",
        doi="10.1234/example",
        source="openalex",
    )

    paper2 = PaperRecord(
        id="2",
        title="A different title",
        doi="10.1234/example",
        source="crossref",
    )

    observation = Observation(
        status="success",
        papers=[paper1, paper2],
    )

    update_state(state, None, observation)

    assert len(state.papers) == 1
    assert state.papers[0].doi == "10.1234/example"


def test_update_state_trace():
    """Les observations et les traces sont enregistrées."""

    state = SearchState(
        objective="Research",
        queries={},
    )

    observation = Observation(
        status="empty",
        tool="openalex",
    )

    update_state(state, None, observation)

    assert state.step == 1
    assert len(state.observations) == 1
    assert len(state.trace) == 1
    assert state.trace[0].step == 1
