
def _format_group(concepts: list[str]) -> str:
    """Construit un groupe de concepts reliés par OR."""

    cleaned = []
    seen = set()

    for concept in concepts:
        concept = " ".join(concept.split()).strip()

        if not concept:
            continue

        normalized = concept.casefold()

        if normalized not in seen:
            cleaned.append(concept)
            seen.add(normalized)

    if not cleaned:
        return ""

    expressions = [
        f'"{concept.replace(chr(34), chr(92) + chr(34))}"'
        for concept in cleaned
    ]

    if len(expressions) == 1:
        return expressions[0]

    return "(" + " OR ".join(expressions) + ")"


def build_queries(
    technologies: list[str],
    domain_concepts: list[str],
    research_tasks: list[str]
) -> dict[str, str]:
    """
    Construit des requêtes booléennes à partir des concepts
    extraits des Research Questions.
    """

    groups = [
        _format_group(technologies),
        _format_group(domain_concepts),
        _format_group(research_tasks)
    ]

    # Ignorer les catégories vides.
    groups = [group for group in groups if group]

    if not groups:
        raise ValueError(
            "Aucun concept disponible pour construire les requêtes."
        )

    base_query = " AND ".join(groups)

    return {
        "openalex": base_query,
        "crossref": base_query,
        "semantic_scholar": base_query,
    }
