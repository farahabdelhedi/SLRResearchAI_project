
import re
import unicodedata

from slrresearch.core.react.contracts import PaperRecord
from slrresearch.schemas.screening import (
    DeduplicationResult,
    DuplicateGroup,
)


def normalize_doi(doi: str) -> str:
    """Normalise un DOI pour faciliter la comparaison."""

    value = doi.strip().lower()

    value = re.sub(
        r"^https?://(dx\.)?doi\.org/",
        "",
        value,
    )

    value = value.removeprefix("doi:")

    return value.strip()


def normalize_title(title: str) -> str:
    """Normalise un titre pour détecter les titres identiques."""

    value = unicodedata.normalize("NFKC", title)
    value = value.casefold()

    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def paper_information_score(paper: PaperRecord) -> int:
    """Évalue la quantité d'informations disponibles sur un article."""

    score = 0

    if paper.title.strip():
        score += 1

    if paper.abstract.strip():
        score += 3

    if paper.doi.strip():
        score += 2

    if paper.url.strip():
        score += 1

    if paper.open_access:
        score += 1

    return score


def deduplicate_papers(
    papers: list[PaperRecord],
) -> DeduplicationResult:
    """Détecte les doublons et conserve le meilleur exemplaire."""

    groups: dict[tuple[str, str], list[PaperRecord]] = {}

    for paper in papers:
        doi = normalize_doi(paper.doi)

        title = normalize_title(paper.title)

        if doi:
            key = ("doi", doi)

        elif title:
            key = ("title", title)

        else:
            identifier = paper.id.strip().casefold()
            source = paper.source.strip().casefold()
            key = ("identifier", f"{source}:{identifier}")

        groups.setdefault(key, []).append(paper)

    unique_papers = []
    duplicate_groups = []

    for (match_type, _), group in groups.items():

        # L'article le plus complet est conservé.
        canonical = max(
            group,
            key=paper_information_score,
        )

        unique_papers.append(canonical)

        duplicates = [
            paper.id
            for paper in group
            if paper.id != canonical.id
        ]

        if duplicates:
            duplicate_groups.append(
                DuplicateGroup(
                    canonical_paper_id=canonical.id,
                    duplicate_paper_ids=duplicates,
                    match_type=match_type,
                )
            )

    return DeduplicationResult(
        unique_papers=unique_papers,
        duplicate_groups=duplicate_groups,
        total_input=len(papers),
        total_unique=len(unique_papers),
    )
