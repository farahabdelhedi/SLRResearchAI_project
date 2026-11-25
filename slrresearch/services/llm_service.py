
"""
Service centralisé pour les interactions avec les modèles LLM.

Responsabilités :
- Exécuter les appels au modèle via LangChain.
- Mesurer le temps d'exécution.
- Récupérer les métadonnées disponibles.
- Retourner une réponse standardisée.

Ce service est partagé entre les différents agents du projet.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass
class LLMResponse:
    """
    Résultat standardisé d'un appel au LLM.

    Contient le texte généré et les informations observables
    concernant l'exécution.
    """

    content: str
    provider: str
    latency_seconds: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None


def extract_metadata(response: Any) -> tuple[
    int | None,
    int | None,
    str | None,
]:
    """
    Extrait les métadonnées disponibles dans une réponse LangChain.

    Les métadonnées dépendent du fournisseur et du modèle utilisés.
    Elles peuvent donc être absentes.
    """

    usage = getattr(response, "usage_metadata", None) or {}
    metadata = getattr(response, "response_metadata", None) or {}

    return (
        usage.get("input_tokens"),
        usage.get("output_tokens"),
        metadata.get("finish_reason") or metadata.get("done_reason"),
    )


def invoke_model(
    model: Any,
    messages: Any,
    provider: str = "demo",
) -> LLMResponse:
    """
    Exécute un appel au modèle et retourne une réponse standardisée.

    Args:
        model: modèle LangChain configuré.
        messages: prompt texte ou liste de messages.
        provider: nom du fournisseur du modèle.

    Returns:
        LLMResponse contenant le texte et les métadonnées.
    """

    started = perf_counter()

    response = model.invoke(messages)

    latency = perf_counter() - started

    content = str(response.content).strip()

    input_tokens, output_tokens, finish_reason = extract_metadata(
        response
    )

    return LLMResponse(
        content=content,
        provider=provider,
        latency_seconds=latency,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reason=finish_reason,
    )
