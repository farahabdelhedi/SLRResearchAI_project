
from dataclasses import dataclass

from slrresearch.schemas.screening import (
    ScreeningDecision,
    SemanticScreeningResult,
    LLMScreeningDecision,
    ComparisonResult,
)


@dataclass(frozen=True)
class SemanticFusionConfig:
    """
    Configuration facultative pour interpréter les similarités.

    Les seuils doivent être définis et validés à partir
    de décisions humaines annotées.
    """

    inclusion_threshold: float | None = None
    exclusion_threshold: float | None = None
    min_margin: float = 0.05

    def __post_init__(self):
        if not 0 <= self.min_margin <= 2:
            raise ValueError("min_margin doit être compris entre 0 et 2.")

        if (self.inclusion_threshold is None) != (
            self.exclusion_threshold is None
        ):
            raise ValueError(
                "Les deux seuils sémantiques doivent être définis ensemble."
            )

        for threshold in (
            self.inclusion_threshold,
            self.exclusion_threshold,
        ):
            if threshold is not None and not -1 <= threshold <= 1:
                raise ValueError(
                    "Les seuils doivent être compris entre -1 et 1."
                )


def _get_semantic_signal(
    semantic_result: SemanticScreeningResult,
    config: SemanticFusionConfig,
) -> str | None:
    """
    Interprète les similarités uniquement si des seuils
    validés ont été configurés.

    Retourne : include, exclude ou None.
    """

    if config.inclusion_threshold is None:
        return None

    inclusion_scores = [
        item.similarity
        for item in semantic_result.inclusion_scores
    ]

    exclusion_scores = [
        item.similarity
        for item in semantic_result.exclusion_scores
    ]

    if not inclusion_scores and not exclusion_scores:
        return None

    max_inclusion = (
        max(inclusion_scores) if inclusion_scores else None
    )
    max_exclusion = (
        max(exclusion_scores) if exclusion_scores else None
    )

    include_supported = (
        max_inclusion is not None
        and max_inclusion >= config.inclusion_threshold
        and (
            max_exclusion is None
            or max_inclusion - max_exclusion >= config.min_margin
        )
    )

    exclude_supported = (
        max_exclusion is not None
        and max_exclusion >= config.exclusion_threshold
        and (
            max_inclusion is None
            or max_exclusion - max_inclusion >= config.min_margin
        )
    )

    if include_supported and not exclude_supported:
        return "include"

    if exclude_supported and not include_supported:
        return "exclude"

    return None


def fuse_screening_results(
    deterministic: ScreeningDecision,
    semantic: SemanticScreeningResult,
    llm: LLMScreeningDecision,
    config: SemanticFusionConfig | None = None,
) -> ComparisonResult:
    """
    Fusionne les trois analyses d'un article.

    La fusion ne calcule pas une moyenne des scores.
    Les désaccords et les situations incertaines sont
    transmis à la validation humaine.
    """

    config = config or SemanticFusionConfig()

    # 1. Vérifier que les résultats concernent le même article.
    paper_ids = {
        deterministic.paper_id,
        semantic.paper_id,
        llm.paper_id,
    }

    if len(paper_ids) != 1:
        raise ValueError(
            "Les trois résultats ne concernent pas le même article."
        )

    # 2. Déterminer le signal sémantique éventuel.
    semantic_signal = _get_semantic_signal(semantic, config)

    # 3. Détecter les situations nécessitant une revue humaine.
    reasons = []

    if llm.decision == "uncertain":
        reasons.append("Le LLM n'a pas pu prendre une décision claire.")

    if not deterministic.indicators.information_sufficient:
        reasons.append("Les informations de l'article sont insuffisantes.")

    if deterministic.indicators.conflict:
        reasons.append(
            "Des indicateurs d'inclusion et d'exclusion sont en conflit."
        )

    if deterministic.decision != llm.decision:
        reasons.append(
            "Désaccord entre l'analyse déterministe et l'analyse LLM."
        )

    if (
        semantic_signal is not None
        and semantic_signal != llm.decision
    ):
        reasons.append(
            "Le signal sémantique contredit la décision du LLM."
        )

    if (
        deterministic.decision == "include"
        and deterministic.indicators.exclusion_matches
    ):
        reasons.append(
            "Des indicateurs d'exclusion ont été détectés."
        )

    if (
        deterministic.decision == "exclude"
        and not deterministic.indicators.exclusion_matches
    ):
        reasons.append(
            "L'exclusion n'est pas justifiée par un indicateur d'exclusion."
        )

    # 4. Prendre la décision finale.
    if reasons:
        final_decision = "uncertain"
    elif (
        deterministic.decision == "include"
        and llm.decision == "include"
    ):
        final_decision = "include"
    elif (
        deterministic.decision == "exclude"
        and llm.decision == "exclude"
    ):
        final_decision = "exclude"
    else:
        final_decision = "uncertain"
        reasons.append("Aucune décision automatique suffisamment fiable.")

    # 5. Construire le résultat de comparaison.
    agreement = (
        deterministic.decision == llm.decision
        and (
            semantic_signal is None
            or semantic_signal == llm.decision
        )
    )

    return ComparisonResult(
        paper_id=deterministic.paper_id,
        deterministic_decision=deterministic,
        semantic_result=semantic,
        llm_decision=llm,
        final_decision=final_decision,
        agreement=agreement,
        needs_human_review=(final_decision == "uncertain"),
        escalation_reason=(
            " ".join(reasons) if reasons else None
        ),
    )
