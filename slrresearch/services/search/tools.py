
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import json

import httpx


# ============================================================
# 1. CONTRAT COMMUN DES OUTILS DE RECHERCHE
# ============================================================

SearchCallable = Callable[[str, int], list[dict]]


@dataclass(frozen=True)
class SearchTool:
    """Représente un outil de recherche scientifique."""

    name: str
    search: SearchCallable


# ============================================================
# 2. REGISTRE DES OUTILS AUTORISÉS
# ============================================================

class ToolNotAllowedError(ValueError):
    """Erreur lorsqu'un outil non autorisé est demandé."""

    pass


class ToolRegistry:
    """Liste blanche des outils que le runtime autorise."""

    def __init__(self, tools: list[SearchTool]):
        self._tools = {tool.name: tool for tool in tools}

    @property
    def names(self) -> list[str]:
        """Retourne les noms des outils disponibles."""
        return list(self._tools)

    def authorize(self, tool_name: str | None) -> SearchTool:
        """Retourne uniquement un outil enregistré."""

        if tool_name is None or tool_name not in self._tools:
            raise ToolNotAllowedError(
                f"Outil non autorisé : {tool_name}"
            )

        return self._tools[tool_name]


# ============================================================
# 3. BACKEND LOCAL POUR LES TESTS
# ============================================================

def load_catalog_backend(path: Path, source: str) -> SearchCallable:
    """
    Backend local reproductible utilisé par les tests
    et les démonstrations sans connexion Internet.
    """

    records = json.loads(path.read_text(encoding="utf-8"))

    def search(query: str, limit: int) -> list[dict]:

        tokens = {
            token.lower().strip('()"')
            for token in query.replace("AND", " ").replace("OR", " ").split()
            if len(token.strip('()"')) > 2
        }

        matches = []

        for item in records:
            if item["source"] != source:
                continue

            haystack = (
                f'{item["title"]} {item.get("abstract", "")}'
            ).lower()

            if not tokens or any(token in haystack for token in tokens):
                matches.append({
                    key: value
                    for key, value in item.items()
                    if key != "source"
                })

        return matches[:limit]

    return search


# ============================================================
# 4. OPENALEX API
# ============================================================

def openalex_search(query: str, limit: int) -> list[dict]:
    """Recherche des articles scientifiques avec OpenAlex."""

    response = httpx.get(
        "https://api.openalex.org/works",
        params={
            "search": query,
            "per-page": limit,
        },
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    return [
        {
            "id": item["id"].rsplit("/", 1)[-1],
            "title": item.get("title") or "Sans titre",
            "abstract": reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
            "doi": item.get("doi") or "",
            "url": (
                (item.get("best_oa_location") or {}).get("pdf_url")
                or (item.get("primary_location") or {}).get("landing_page_url")
                or item["id"]
            ),
            "open_access": bool(
                (item.get("open_access") or {}).get("is_oa")
            ),
        }
        for item in data.get("results", [])
    ]
def reconstruct_openalex_abstract(inverted_index: dict | None) -> str:
    """Reconstruit un abstract OpenAlex à partir de son index inversé."""

    if not isinstance(inverted_index, dict):
        return ""

    words_by_position = {}

    for word, positions in inverted_index.items():
        for position in positions:
            if isinstance(position, int):
                words_by_position[position] = word

    return " ".join(
        words_by_position[position]
        for position in sorted(words_by_position)
    )

# ============================================================
# 5. CROSSREF API
# ============================================================

def crossref_search(query: str, limit: int) -> list[dict]:
    """Recherche des articles scientifiques avec Crossref."""

    response = httpx.get(
        "https://api.crossref.org/works",
        params={
            "query.bibliographic": query,
            "rows": limit,
        },
        timeout=20,
    )

    response.raise_for_status()
    items = response.json()["message"]["items"]

    return [
        {
            "id": item.get("DOI") or item.get("URL", ""),
            "title": (item.get("title") or ["Sans titre"])[0],
            "abstract": item.get("abstract", "") or "",
            "doi": item.get("DOI", "") or "",
            "url": item.get("URL", "") or "",
            "open_access": bool(item.get("license")),
        }
        for item in items
    ]


# ============================================================
# 6. SEMANTIC SCHOLAR API
# ============================================================

def semantic_scholar_search(query: str, limit: int) -> list[dict]:
    """Recherche des articles scientifiques avec Semantic Scholar."""

    response = httpx.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={
            "query": query,
            "limit": limit,
            "fields": (
                "title,abstract,externalIds,openAccessPdf,url"
            ),
        },
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    papers = []

    for item in data.get("data", []):

        external_ids = item.get("externalIds") or {}
        pdf_info = item.get("openAccessPdf") or {}

        papers.append({
            "id": item.get("paperId") or "",
            "title": item.get("title") or "Sans titre",
            "abstract": item.get("abstract") or "",
            "doi": external_ids.get("DOI") or "",
            "url": pdf_info.get("url") or item.get("url") or "",
            "open_access": bool(pdf_info.get("url")),
        })

    return papers
