
from slrresearch.core.react.contracts import PaperRecord
from slrresearch.services.screening.deduplication import (
    deduplicate_papers,
    normalize_doi,
    normalize_title,
)


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1234/ABC") == "10.1234/abc"
    assert normalize_doi(" DOI:10.1234/ABC ") == "10.1234/abc"


def test_normalize_title():
    assert normalize_title("Artificial Intelligence: An Introduction") == (
        "artificial intelligence an introduction"
    )


def test_deduplicate_by_doi():
    papers = [
        PaperRecord(
            id="1",
            title="Paper A",
            doi="10.1234/ABC",
            source="openalex",
        ),
        PaperRecord(
            id="2",
            title="Paper A - another version",
            doi="https://doi.org/10.1234/abc",
            source="crossref",
        ),
    ]

    result = deduplicate_papers(papers)

    assert result.total_input == 2
    assert result.total_unique == 1
    assert result.duplicate_groups[0].match_type == "doi"


def test_deduplicate_by_title():
    papers = [
        PaperRecord(
            id="1",
            title="Artificial Intelligence: An Introduction",
            source="openalex",
        ),
        PaperRecord(
            id="2",
            title="ARTIFICIAL INTELLIGENCE An Introduction!",
            source="crossref",
        ),
    ]

    result = deduplicate_papers(papers)

    assert result.total_unique == 1
    assert result.duplicate_groups[0].match_type == "title"


def test_keep_most_complete_paper():
    papers = [
        PaperRecord(
            id="1",
            title="Paper A",
            doi="10.1234/abc",
            source="openalex",
        ),
        PaperRecord(
            id="2",
            title="Paper A",
            abstract="This is a scientific abstract.",
            doi="10.1234/abc",
            url="https://example.com/paper.pdf",
            source="crossref",
            open_access=True,
        ),
    ]

    result = deduplicate_papers(papers)

    assert result.total_unique == 1
    assert result.unique_papers[0].id == "2"


def test_no_duplicates():
    papers = [
        PaperRecord(id="1", title="Paper A", source="openalex"),
        PaperRecord(id="2", title="Paper B", source="crossref"),
    ]

    result = deduplicate_papers(papers)

    assert result.total_input == 2
    assert result.total_unique == 2
    assert result.duplicate_groups == []
