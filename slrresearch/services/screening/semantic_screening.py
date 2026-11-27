
from langchain_ollama import OllamaEmbeddings
import numpy as np

from slrresearch.core.react.contracts import PaperRecord
from slrresearch.schemas.screening import (
    ScreeningCriteria,
    SemanticScreeningResult,
    CriterionSimilarity,
)


class SemanticScreeningService:
    """
    Service de screening sémantique basé sur les embeddings Ollama.

    Il compare le contenu des articles aux critères
    d'inclusion et d'exclusion.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text:latest",
    ):
        self.embeddings = OllamaEmbeddings(model=model)

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """Calcule la similarité cosinus entre deux vecteurs."""

        a = np.array(vector_a, dtype=float)
        b = np.array(vector_b, dtype=float)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def compare_texts(
        self,
        paper_text: str,
        criterion: str,
    ) -> float:
        """Compare un article avec un critère."""

        if not paper_text.strip() or not criterion.strip():
            raise ValueError(
                "Le texte de l'article et le critère sont obligatoires."
            )

        vectors = self.embeddings.embed_documents(
            [paper_text, criterion]
        )

        return self.cosine_similarity(
            vectors[0],
            vectors[1],
        )

    def analyze_paper(
        self,
        paper: PaperRecord,
        criteria: ScreeningCriteria,
        ) -> SemanticScreeningResult:
        """
        Calcule la similarité entre un article
        et chaque critère d'inclusion et d'exclusion.
        """

        paper_text = f"{paper.title} {paper.abstract}".strip()

        if not paper_text:
            raise ValueError(
                f"L'article {paper.id} ne contient aucune information."
            )

        # Regrouper tous les critères dans une seule liste.
        all_criteria = (
            criteria.inclusion_criteria
            + criteria.exclusion_criteria
        )

        if not all(criterion.strip() for criterion in all_criteria):
            raise ValueError("Un critère ne peut pas être vide.")

        # Calculer tous les embeddings en une seule opération.
        texts = [paper_text] + all_criteria
        try:
            vectors = self.embeddings.embed_documents(texts)

        except Exception as error:
            raise RuntimeError(
                "Impossible de calculer les embeddings. "
                "Vérifiez que Ollama est démarré et que le modèle "
                "'nomic-embed-text:latest' est disponible."
            ) from error
        if len(vectors) != len(texts):
            raise RuntimeError(
                "Le nombre d'embeddings retournés ne correspond "
                "pas au nombre de textes fournis."
            )
        paper_vector = vectors[0]
        criterion_vectors = vectors[1:]

        # Séparer les résultats des critères d'inclusion.
        inclusion_scores = [
            {
                "criterion": criterion,
                "similarity": self.cosine_similarity(
                    paper_vector,
                    criterion_vector,
                ),
            }
            for criterion, criterion_vector in zip(
                criteria.inclusion_criteria,
                criterion_vectors[:len(criteria.inclusion_criteria)],
            )
        ]

        # Séparer les résultats des critères d'exclusion.
        exclusion_scores = [
            {
                "criterion": criterion,
                "similarity": self.cosine_similarity(
                    paper_vector,
                    criterion_vector,
                ),
            }
            for criterion, criterion_vector in zip(
                criteria.exclusion_criteria,
                criterion_vectors[len(criteria.inclusion_criteria):],
            )
        ]

        return SemanticScreeningResult(
            paper_id=paper.id,
            inclusion_scores=[
                CriterionSimilarity(**item)
                for item in inclusion_scores
            ],
            exclusion_scores=[
                CriterionSimilarity(**item)
                for item in exclusion_scores
            ],
        )