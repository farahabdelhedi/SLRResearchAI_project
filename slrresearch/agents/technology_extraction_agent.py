
import json
import re

from slrresearch.prompts.technology_extraction_prompts import (
    build_technology_extraction_prompt
)
from slrresearch.schemas.query_construction import (
    TechnologyExtractionResult
)


class TechnologyExtractionAgent:
    def __init__(self, model):
        self.model = model

    def extract(self, questions: list) -> TechnologyExtractionResult:
        if not questions:
            raise ValueError(
                "Au moins une Research Question approuvée est nécessaire."
            )

        prompt = build_technology_extraction_prompt(questions)

        response = self.model.invoke(prompt)

        content = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        content = content.strip()

        # Supprimer les éventuels blocs Markdown autour du JSON.
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(r"\s*```$", "", content)

        # Convertir la réponse JSON en dictionnaire Python.
        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Le LLM a retourné un résultat JSON invalide."
            ) from error

        # Valider la structure du résultat.
        try:
            result = TechnologyExtractionResult.model_validate(data)
        except Exception as error:
            raise ValueError(
                "Le résultat de l'extraction des concepts est invalide."
            ) from error

        # Nettoyer les espaces et supprimer les doublons.
        for category in (
            "technologies",
            "domain_concepts",
            "research_tasks"
        ):
            cleaned_values = []
            seen = set()

            for value in getattr(result, category):
                value = " ".join(value.split()).strip()

                if not value:
                    continue

                normalized = value.casefold()

                if normalized not in seen:
                    cleaned_values.append(value)
                    seen.add(normalized)

            setattr(result, category, cleaned_values)

        # Vérifier qu'au moins une catégorie contient un concept.
        if not any([
            result.technologies,
            result.domain_concepts,
            result.research_tasks
        ]):
            raise ValueError(
                "Aucun concept pertinent n'a été extrait."
            )

        return result
