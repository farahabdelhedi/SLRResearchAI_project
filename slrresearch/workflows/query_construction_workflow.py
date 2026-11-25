
from slrresearch.agents.technology_extraction_agent import (
    TechnologyExtractionAgent
)
from slrresearch.services.query_builder import build_queries
from slrresearch.schemas.query_construction import QueryConstructionResult


class QueryConstructionWorkflow:
    def __init__(self, technology_agent: TechnologyExtractionAgent):
        self.technology_agent = technology_agent

    def run(self, approved_questions: list) -> QueryConstructionResult:
        if not approved_questions:
            raise ValueError(
                "Aucune Research Question approuvée n'a été fournie."
            )

        # 1. Extraire les trois catégories de concepts.
        extraction = self.technology_agent.extract(approved_questions)

        # 2. Construire les requêtes booléennes.
        queries = build_queries(
            technologies=extraction.technologies,
            domain_concepts=extraction.domain_concepts,
            research_tasks=extraction.research_tasks
        )

        # 3. Retourner le résultat complet.
        return QueryConstructionResult(
            technologies=extraction.technologies,
            domain_concepts=extraction.domain_concepts,
            research_tasks=extraction.research_tasks,
            queries=queries
        )
