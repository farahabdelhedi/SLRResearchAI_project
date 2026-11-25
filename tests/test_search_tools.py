
from unittest.mock import Mock

from slrresearch.services.search.tools import (
    openalex_search,
    crossref_search,
    semantic_scholar_search,
)


def test_openalex_search(monkeypatch):
    """Vérifier la normalisation des résultats OpenAlex."""

    response = Mock()
    response.json.return_value = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "title": "LLM in Education",
                "doi": "https://doi.org/10.1234/example",
                "best_oa_location": {
                    "pdf_url": "https://example.com/paper.pdf"
                },
                "open_access": {"is_oa": True},
            }
        ]
    }
    response.raise_for_status.return_value = None

    def fake_get(url, params, timeout):
        assert url == "https://api.openalex.org/works"
        assert params["search"] == "LLM Education"
        return response

    monkeypatch.setattr(
        "slrresearch.services.search.tools.httpx.get",
        fake_get,
    )

    papers = openalex_search("LLM Education", 5)

    assert len(papers) == 1
    assert papers[0]["id"] == "W123"
    assert papers[0]["title"] == "LLM in Education"
    assert papers[0]["open_access"] is True


def test_crossref_search(monkeypatch):
    """Vérifier la normalisation des résultats Crossref."""

    response = Mock()
    response.json.return_value = {
        "message": {
            "items": [
                {
                    "DOI": "10.1234/example",
                    "title": ["LLM in Education"],
                    "abstract": "An example abstract.",
                    "URL": "https://doi.org/10.1234/example",
                    "license": [{"URL": "https://example.com/license"}],
                }
            ]
        }
    }
    response.raise_for_status.return_value = None

    def fake_get(url, params, timeout):
        assert url == "https://api.crossref.org/works"
        assert params["query.bibliographic"] == "LLM Education"
        return response

    monkeypatch.setattr(
        "slrresearch.services.search.tools.httpx.get",
        fake_get,
    )

    papers = crossref_search("LLM Education", 5)

    assert len(papers) == 1
    assert papers[0]["id"] == "10.1234/example"
    assert papers[0]["title"] == "LLM in Education"
    assert papers[0]["abstract"] == "An example abstract."


def test_semantic_scholar_search(monkeypatch):
    """Vérifier la normalisation des résultats Semantic Scholar."""

    response = Mock()
    response.json.return_value = {
        "data": [
            {
                "paperId": "abc123",
                "title": "LLM in Education",
                "abstract": "An example abstract.",
                "externalIds": {"DOI": "10.1234/example"},
                "openAccessPdf": {
                    "url": "https://example.com/paper.pdf"
                },
                "url": "https://www.semanticscholar.org/paper/abc123",
            }
        ]
    }
    response.raise_for_status.return_value = None

    def fake_get(url, params, timeout):
        assert url == "https://api.semanticscholar.org/graph/v1/paper/search"
        assert params["query"] == "LLM Education"
        return response

    monkeypatch.setattr(
        "slrresearch.services.search.tools.httpx.get",
        fake_get,
    )

    papers = semantic_scholar_search("LLM Education", 5)

    assert len(papers) == 1
    assert papers[0]["id"] == "abc123"
    assert papers[0]["title"] == "LLM in Education"
    assert papers[0]["open_access"] is True
