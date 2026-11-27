
import json

from slrresearch.prompts.screening_criteria_prompts import (
    build_screening_criteria_prompt,
)
from slrresearch.schemas.screening import ScreeningCriteria
from slrresearch.services.llm_service import invoke_model


class CriteriaGenerationAgent:
    """
    Agent chargé de générer les critères d'inclusion et d'exclusion
    à partir de l'objectif de la SLR et des Research Questions approuvées.
    """

    def __init__(self, model, provider="demo"):
        self.model = model
        self.provider = provider

    def generate(
        self,
        objective: str,
        approved_questions: list,
    ) -> ScreeningCriteria:

        prompt = build_screening_criteria_prompt(
            objective=objective,
            approved_questions=approved_questions,
        )

        response = invoke_model(
            model=self.model,
            messages=prompt,
            provider=self.provider,
        )

        if hasattr(response, "content"):
            response = response.content

        if not isinstance(response, str):
            raise ValueError("La réponse du LLM doit être une chaîne de caractères.")

        content = response.strip()

        # Supprimer les éventuelles balises Markdown JSON.
        if content.startswith("```"):
            content = content.replace("```json", "", 1)
            content = content.replace("```", "").strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Le LLM n'a pas retourné un JSON valide pour les critères."
            ) from exc

        return ScreeningCriteria.model_validate(data)
