
import json
import re

from langchain_core.messages import HumanMessage

from slrresearch.prompts.llm_screening_prompts import (
    build_llm_screening_prompt,
)

from slrresearch.schemas.screening import (
    ScreeningCriteria,
    LLMScreeningDecision,
)

from slrresearch.core.react.contracts import PaperRecord

from slrresearch.services.llm_service import invoke_model


class LLMScreeningAgent:
    """
    Agent responsable de l'analyse approfondie
    des articles scientifiques par un LLM.
    """

    def __init__(self, model, provider: str = "demo"):
        self.model = model
        self.provider = provider

    def analyze(
        self,
        paper: PaperRecord,
        criteria: ScreeningCriteria,
    ) -> LLMScreeningDecision:
        """
        Analyse un article selon les critères approuvés.

        Le LLM évalue chaque critère individuellement,
        fournit des preuves et retourne une décision globale.
        """

        # 1. Construire le prompt.
        prompt = build_llm_screening_prompt(
            paper=paper,
            criteria=criteria,
        )

        # 2. Envoyer le prompt au LLM.
        try:
            response = invoke_model(
                model=self.model,
                messages=[
                    HumanMessage(content=prompt)
                ],
                provider=self.provider,
            )
        except Exception as error:
            raise RuntimeError(
                f"Échec de l'analyse LLM de l'article {paper.id}."
            ) from error

        # 3. Récupérer le contenu de la réponse.
        content = response.content.strip()

        
        # 4. Nettoyer et extraire le JSON de la réponse.
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )
        content = re.sub(r"\s*```$", "", content)

        # 5. Extraire le JSON même si le LLM ajoute du texte autour.
        try:
            json_start = content.find("{")

            if json_start == -1:
                raise ValueError("Aucun objet JSON trouvé dans la réponse.")

            data, _ = json.JSONDecoder().raw_decode(
                content[json_start:]
            )

        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                "Le LLM a retourné un JSON invalide."
            ) from error


        # 6. Vérifier et valider la structure Pydantic.
        try:
            decision = LLMScreeningDecision.model_validate(data)
        except Exception as error:
            raise ValueError(
                "La décision retournée par le LLM "
                "ne respecte pas le schéma attendu."
            ) from error

        # 7. Vérifier que la décision concerne le bon article.
        if decision.paper_id != paper.id:
            raise ValueError(
                "L'identifiant de l'article retourné par le LLM "
                "ne correspond pas à l'article analysé."
            )

        # 8. Vérifier que tous les critères ont été évalués.
        expected_criteria = (
            criteria.inclusion_criteria
            + criteria.exclusion_criteria
        )

        assessed_criteria = [
            assessment.criterion
            for assessment in decision.criterion_assessments
        ]
        print("\n========== VÉRIFICATION DES CRITÈRES ==========")
        print("CRITÈRES ATTENDUS :")
        for i, criterion in enumerate(expected_criteria):
            print(f"{i}: {repr(criterion)}")

        print("\nCRITÈRES ÉVALUÉS PAR LE LLM :")
        for i, criterion in enumerate(assessed_criteria):
            print(f"{i}: {repr(criterion)}")

        print("===============================================\n")
        if assessed_criteria != expected_criteria:
            raise ValueError(
                "Le LLM n'a pas évalué tous les critères "
                "dans l'ordre attendu."
            )

        # 9. Retourner la décision validée.
        return decision
