
"""
Agent orchestrateur du screening titre-résumé.

Il coordonne :
- la déduplication ;
- le screening déterministe ;
- le screening sémantique ;
- l'analyse LLM ;
- la fusion des résultats.
"""

from slrresearch.core.react.contracts import (
    PaperRecord,
    SearchState,
)

from slrresearch.schemas.screening import (
    ScreeningCriteria,
    ScreeningResult,
)

from slrresearch.agents.llm_screening_agent import (
    LLMScreeningAgent,
)

from slrresearch.services.screening.deduplication import (
    deduplicate_papers,
)

from slrresearch.services.screening.deterministic_screening import (
    screen_paper_deterministically,
)

from slrresearch.services.screening.semantic_screening import (
    SemanticScreeningService,
)

from slrresearch.services.screening.screening_fusion import (
    SemanticFusionConfig,
    fuse_screening_results,
)


class ScreeningAgent:
    """
    Orchestre le screening des articles après la recherche bibliographique.
    """

    def __init__(
        self,
        llm_agent: LLMScreeningAgent,
        semantic_service: SemanticScreeningService | None = None,
        fusion_config: SemanticFusionConfig | None = None,
        embedding_model: str = "nomic-embed-text:latest",
    ):
        self.llm_agent = llm_agent

        self.semantic_service = (
            semantic_service
            if semantic_service is not None
            else SemanticScreeningService(model=embedding_model)
        )

        self.fusion_config = (
            fusion_config
            if fusion_config is not None
            else SemanticFusionConfig()
        )

    def run(
        self,
        papers: list[PaperRecord] | SearchState,
        criteria: ScreeningCriteria,
    ) -> ScreeningResult:
        """
        Lance le screening titre-résumé.

        Args:
            papers:
                Liste d'articles ou SearchState retourné
                par SearchExecutionAgent.

            criteria:
                Critères de screening validés par le chercheur.

        Returns:
            ScreeningResult contenant les décisions,
            la file de révision humaine et les articles retenus.
        """

        # 1. Récupérer les articles depuis le SearchState
        #    ou utiliser directement la liste fournie.
        if isinstance(papers, SearchState):
            paper_list = papers.papers
        else:
            paper_list = papers

        # 2. Supprimer les doublons.
        deduplication = deduplicate_papers(paper_list)

        unique_papers = deduplication.unique_papers

        comparisons = []
        human_review_queue = []
        selected_papers = []

        # 3. Analyser chaque article unique.
        for paper in unique_papers:

            # Screening déterministe
            deterministic_decision = (
                screen_paper_deterministically(
                    paper=paper,
                    include_terms=criteria.inclusion_terms,
                    exclude_terms=criteria.exclusion_terms,
                )
            )

            # Screening sémantique
            semantic_result = (
                self.semantic_service.analyze_paper(
                    paper=paper,
                    criteria=criteria,
                )
            )

            # Analyse LLM
            llm_decision = self.llm_agent.analyze(
                paper=paper,
                criteria=criteria,
            )

            # Fusion des trois résultats
            comparison = fuse_screening_results(
                deterministic=deterministic_decision,
                semantic=semantic_result,
                llm=llm_decision,
                config=self.fusion_config,
            )

            comparisons.append(comparison)

            # 4. Ajouter les articles nécessitant
            #    une vérification humaine.
            if (
                comparison.needs_human_review
                or comparison.final_decision == "uncertain"
            ):
                human_review_queue.append(paper.id)

            # 5. Conserver les articles inclus.
            if comparison.final_decision == "include":
                selected_papers.append(paper)

        # 6. Construire le résultat global.
        return ScreeningResult(
            deduplication=deduplication,
            title_abstract_decisions=comparisons,
            human_review_queue=human_review_queue,
            selected_papers=selected_papers,
        )
