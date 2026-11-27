
import pytest

from slrresearch.services.screening.semantic_screening import (
    SemanticScreeningService,
)
from slrresearch.core.react.contracts import PaperRecord
from slrresearch.schemas.screening import ScreeningCriteria


def test_cosine_similarity_identical_vectors():
    score = SemanticScreeningService.cosine_similarity(
        [1, 0, 1],
        [1, 0, 1],
    )

    assert score == pytest.approx(1.0)


def test_cosine_similarity_opposite_vectors():
    score = SemanticScreeningService.cosine_similarity(
        [1, 0],
        [-1, 0],
    )

    assert score == pytest.approx(-1.0)


def test_cosine_similarity_orthogonal_vectors():
    score = SemanticScreeningService.cosine_similarity(
        [1, 0],
        [0, 1],
    )

    assert score == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    score = SemanticScreeningService.cosine_similarity(
        [0, 0],
        [1, 2],
    )

    assert score == 0.0


def test_cosine_similarity_rejects_different_dimensions():
    with pytest.raises(ValueError):
        SemanticScreeningService.cosine_similarity(
            [1, 2],
            [1, 2, 3],
        )

class FakeEmbeddings:
    """Remplace Ollama pendant les tests."""

    def __init__(self):
        self.calls = 0
        self.received_texts = []

    def embed_documents(self, texts):
        self.calls += 1
        self.received_texts = texts

        vectors = {
            "Machine learning medical diagnosis": [1, 1],
            "machine learning": [1, 0],
            "medical diagnosis": [0, 1],
            "animal farming": [-1, 0],
        }

        return [vectors[text] for text in texts]


def create_test_data():
    paper = PaperRecord(
        id="paper-1",
        title="Machine learning",
        abstract="medical diagnosis",
        source="test",
    )

    criteria = ScreeningCriteria(
        inclusion_criteria=[
            "machine learning",
            "medical diagnosis",
        ],
        exclusion_criteria=[
            "animal farming",
        ],
    )

    return paper, criteria


def test_analyze_paper_returns_pydantic_result():
    service = SemanticScreeningService.__new__(
        SemanticScreeningService
    )
    service.embeddings = FakeEmbeddings()

    paper, criteria = create_test_data()

    result = service.analyze_paper(paper, criteria)

    assert result.paper_id == "paper-1"
    assert len(result.inclusion_scores) == 2
    assert len(result.exclusion_scores) == 1

    assert result.inclusion_scores[0].similarity == pytest.approx(
        0.7071, abs=0.001
    )

    assert result.exclusion_scores[0].similarity == pytest.approx(
        -0.7071, abs=0.001
    )


def test_analyze_paper_calculates_embeddings_only_once():
    service = SemanticScreeningService.__new__(
        SemanticScreeningService
    )
    fake_embeddings = FakeEmbeddings()
    service.embeddings = fake_embeddings

    paper, criteria = create_test_data()

    service.analyze_paper(paper, criteria)

    assert fake_embeddings.calls == 1
    assert len(fake_embeddings.received_texts) == 4
class FailingEmbeddings:
    """Simule une panne du service Ollama."""

    def embed_documents(self, texts):
        raise ConnectionError("Ollama is unavailable")


class IncompleteEmbeddings:
    """Simule un retour incomplet d'embeddings."""

    def embed_documents(self, texts):
        return [[0.5, 0.5]]  # Un seul vecteur au lieu de plusieurs
def test_analyze_paper_handles_embedding_error():
    service = SemanticScreeningService.__new__(
        SemanticScreeningService
    )
    service.embeddings = FailingEmbeddings()

    paper, criteria = create_test_data()

    with pytest.raises(
        RuntimeError,
        match="Impossible de calculer les embeddings",
    ):
        service.analyze_paper(paper, criteria)


def test_analyze_paper_rejects_incomplete_embeddings():
    service = SemanticScreeningService.__new__(
        SemanticScreeningService
    )
    service.embeddings = IncompleteEmbeddings()

    paper, criteria = create_test_data()

    with pytest.raises(
        RuntimeError,
        match="Le nombre d'embeddings retournés",
    ):
        service.analyze_paper(paper, criteria)