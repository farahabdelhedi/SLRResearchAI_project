
from slrresearch.core.react.engine import run_react_agent
from slrresearch.core.react.policies import LLMDecisionPolicy
from slrresearch.services.search.tools import (
    SearchTool,
    ToolRegistry,
    openalex_search,
    crossref_search,
    semantic_scholar_search,
)
from slrresearch.schemas.query_construction import QueryConstructionResult


class SearchExecutionAgent:
    """
    Agent spécialisé dans la recherche d'articles scientifiques.

    Il utilise un moteur ReAct pour choisir les sources,
    exécuter les recherches et observer les résultats.
    """

    def __init__(self, model):
        self.model = model

        # Sources bibliographiques autorisées
        self.registry = ToolRegistry([
            SearchTool(
                name="openalex",
                search=openalex_search,
            ),
            SearchTool(
                name="crossref",
                search=crossref_search,
            ),
            SearchTool(
                name="semantic_scholar",
                search=semantic_scholar_search,
            ),
        ])

        # Politique de décision basée sur le LLM
        self.decision_policy = LLMDecisionPolicy(model)

    
    def run(
        self,
        objective: str,
        query_result: QueryConstructionResult,
        max_steps: int = 5,
        target_papers: int = 10,
    ):
        """
        Lance une recherche multi-sources contrôlée.

        Args:
            objective: objectif scientifique de la recherche.
            query_result: résultat de Query Construction.
            max_steps: nombre maximal d'actions ReAct.
            target_papers: nombre cible d'articles.

        Returns:
            SearchState contenant les articles, observations et traces.
        """

        if not query_result.queries:
            raise ValueError(
                "Aucune requête bibliographique disponible."
            )

        return run_react_agent(
            objective=objective,
            queries=query_result.queries,
            registry=self.registry,
            decide=self.decision_policy,
            max_steps=max_steps,
            target_papers=target_papers,
        )

