
from slrresearch.core.react.contracts import PaperRecord
from slrresearch.schemas.screening import (
    ScreeningDecision,
    ScreeningIndicators,
)


def normalize_paper_text(paper: PaperRecord) -> str:
    """Combine le titre et le résumé pour l'analyse."""

    return f"{paper.title} {paper.abstract}".casefold()


def observe_indicators(
    paper: PaperRecord,
    include_terms: list[str],
    exclude_terms: list[str],
) -> ScreeningIndicators:
    """Observe les critères d'inclusion et d'exclusion."""

    text = normalize_paper_text(paper)

    inclusion_matches = [
        term
        for term in include_terms
        if term.casefold() in text
    ]

    exclusion_matches = [
        term
        for term in exclude_terms
        if term.casefold() in text
    ]

    information_sufficient = bool(
        paper.title.strip() and paper.abstract.strip()
    )

    conflict = bool(
        inclusion_matches and exclusion_matches
    )

    return ScreeningIndicators(
        inclusion_matches=inclusion_matches,
        exclusion_matches=exclusion_matches,
        information_sufficient=information_sufficient,
        conflict=conflict,
    )


def choose_preliminary_verdict(
    indicators: ScreeningIndicators,
) -> tuple[str, float]:
    """Applique la politique déterministe de décision."""

    if indicators.exclusion_matches:
        return "exclude", 0.95

    if indicators.inclusion_matches:
        return "include", 0.90

    return "uncertain", 0.45


def apply_screening_policy(
    paper: PaperRecord,
    indicators: ScreeningIndicators,
    human_threshold: float = 0.80,
) -> ScreeningDecision:
    """Construit la décision et identifie les cas à vérifier."""

    decision, confidence = choose_preliminary_verdict(indicators)

    needs_human_review = (
        decision == "uncertain"
        or confidence < human_threshold
        or indicators.conflict
        or not indicators.information_sufficient
    )

    reasons = []

    if indicators.inclusion_matches:
        reasons.append(
            f"Critères d'inclusion détectés : "
            f"{', '.join(indicators.inclusion_matches)}"
        )

    if indicators.exclusion_matches:
        reasons.append(
            f"Critères d'exclusion détectés : "
            f"{', '.join(indicators.exclusion_matches)}"
        )

    if not indicators.information_sufficient:
        reasons.append(
            "Informations insuffisantes : titre ou résumé manquant."
        )

    if indicators.conflict:
        reasons.append(
            "Conflit entre les critères d'inclusion et d'exclusion."
        )

    if not reasons:
        reasons.append(
            "Aucun critère d'inclusion ou d'exclusion détecté."
        )

    return ScreeningDecision(
        paper_id=paper.id,
        decision=decision,
        confidence=confidence,
        reasons=reasons,
        indicators=indicators,
        needs_human_review=needs_human_review,
    )


def screen_paper_deterministically(
    paper: PaperRecord,
    include_terms: list[str],
    exclude_terms: list[str],
    human_threshold: float = 0.80,
) -> ScreeningDecision:
    """Exécute le screening déterministe d'un seul article."""

    indicators = observe_indicators(
        paper,
        include_terms,
        exclude_terms,
    )

    return apply_screening_policy(
        paper,
        indicators,
        human_threshold,
    )


def screen_papers_deterministically(
    papers: list[PaperRecord],
    include_terms: list[str],
    exclude_terms: list[str],
    human_threshold: float = 0.80,
) -> list[ScreeningDecision]:
    """Exécute le screening déterministe sur plusieurs articles."""

    return [
        screen_paper_deterministically(
            paper=paper,
            include_terms=include_terms,
            exclude_terms=exclude_terms,
            human_threshold=human_threshold,
        )
        for paper in papers
    ]
