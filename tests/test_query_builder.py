
from slrresearch.services.query_builder import build_queries


def test_build_queries_with_three_categories():
    result = build_queries(
        technologies=["LLM", "Artificial Intelligence"],
        domain_concepts=["Education", "Higher Education"],
        research_tasks=["Personalized Learning"]
    )

    expected = (
        '("LLM" OR "Artificial Intelligence") AND '
        '("Education" OR "Higher Education") AND '
        '"Personalized Learning"'
    )

    assert result["openalex"] == expected
    assert result["crossref"] == expected
    assert result["semantic_scholar"] == expected


def test_build_queries_with_empty_category():
    result = build_queries(
        technologies=["Blockchain"],
        domain_concepts=["Healthcare"],
        research_tasks=[]
    )

    expected = '"Blockchain" AND "Healthcare"'

    assert result["openalex"] == expected
    assert result["crossref"] == expected
    assert result["semantic_scholar"] == expected


def test_build_queries_with_only_one_category():
    result = build_queries(
        technologies=["CNN"],
        domain_concepts=[],
        research_tasks=[]
    )

    expected = '"CNN"'

    assert result["openalex"] == expected
    assert result["crossref"] == expected
    assert result["semantic_scholar"] == expected


def test_build_queries_removes_duplicates():
    result = build_queries(
        technologies=["LLM", "LLM", "Artificial Intelligence"],
        domain_concepts=["Education", "education"],
        research_tasks=[]
    )

    expected = (
        '("LLM" OR "Artificial Intelligence") AND "Education"'
    )

    assert result["openalex"] == expected
    assert result["crossref"] == expected
    assert result["semantic_scholar"] == expected


def test_build_queries_with_no_concepts():
    try:
        build_queries(
            technologies=[],
            domain_concepts=[],
            research_tasks=[]
        )
        assert False, "Une erreur était attendue."
    except ValueError:
        pass
