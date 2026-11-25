
"""
Agent responsable de la génération et de la validation
des questions de recherche (Research Questions) d'une SLR.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from slrresearch.prompts.research_question_prompts import (
    build_system_prompt,
    build_user_prompt,
    build_repair_prompt,
)

from slrresearch.schemas.research_question import (
    FreeTextQuestions,
    WorkflowOutcome,
)

from slrresearch.services.llm_service import invoke_model

from slrresearch.validators.research_question_validator import (
    extract_non_empty_lines,
    validate_free_text,
    validate_questions,
)


class ResearchQuestionAgent:
    """
    Génère trois Research Questions à partir du sujet,
    de l'objectif et du contexte, puis vérifie leur format.
    """

    def __init__(self, model, provider: str = "demo"):
        self.model = model
        self.provider = provider

    def generate(
        self,
        topic: str,
        objective: str,
        context: str = "",
    ) -> FreeTextQuestions:
        """
        Étape 1 : génération des Research Questions par le LLM.
        """

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(topic, objective, context)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = invoke_model(
            model=self.model,
            messages=messages,
            provider=self.provider,
        )

        return FreeTextQuestions(
            text=response.content,
            provider=response.provider,
            latency_seconds=response.latency_seconds,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            finish_reason=response.finish_reason,
        )

    def repair(self, text: str, error: str):
        """
        Étape 2 : demande au LLM de corriger les questions
        lorsque leur format ne respecte pas les règles.
        """

        repair_prompt = build_repair_prompt(text, error)

        response = invoke_model(
            model=self.model,
            messages=[
                SystemMessage(content=build_system_prompt()),
                HumanMessage(content=repair_prompt),
            ],
            provider=self.provider,
        )

        return response

    def run(
        self,
        topic: str,
        objective: str,
        context: str = "",
    ) -> WorkflowOutcome:
        """
        Étape 3 : workflow complet :
        génération -> validation -> correction éventuelle.
        """

        # 1. Générer les questions
        generated = self.generate(topic, objective, context)

        # 2. Valider le texte généré
        try:
            records = validate_free_text(generated.text)
            questions = validate_questions(records)

            return WorkflowOutcome(
                status="accepted",
                text=generated.text,
                questions=questions,
                repair_attempts=0,
            )

        except (ValueError, TypeError) as first_error:
            error_message = str(first_error)

        # 3. Une seule tentative de correction
        try:
            repaired = self.repair(
                text=generated.text,
                error=error_message,
            )

            records = validate_free_text(repaired.content)
            questions = validate_questions(records)

            return WorkflowOutcome(
                status="repaired",
                text=repaired.content,
                questions=questions,
                repair_attempts=1,
            )

        except (ValueError, TypeError) as repair_error:
            return WorkflowOutcome(
                status="human_required",
                text=generated.text,
                questions=[],
                error=str(repair_error),
                repair_attempts=1,
            )
