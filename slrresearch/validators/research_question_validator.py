
"""
Validateur des Research Questions.

Responsabilités :
- Extraire les lignes non vides.
- Vérifier le format de chaque question.
- Vérifier les identifiants RQ1, RQ2 et RQ3.
- Détecter les questions dupliquées.
- Valider les données avec les schémas Pydantic.
"""

import re

from slrresearch.schemas.research_question import ResearchQuestion


# Format attendu : RQ1. Texte de la question
RQ_PATTERN = re.compile(r"^(RQ[0-9]+)\.\s*(.{15,})$", re.IGNORECASE)


def extract_non_empty_lines(text: str) -> list[str]:
    """Extrait les lignes non vides d'un texte."""

    if not isinstance(text, str):
        raise TypeError("Le contenu doit être une chaîne de caractères.")

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]



def parse_rq_line(line: str) -> dict:
    """Extrait l'identifiant et le texte d'une question."""

    match = re.fullmatch(
        r"^([A-Za-z0-9]+)\.\s*(.{15,})$",
        line.strip()
    )

    if not match:
        raise ValueError(
            f"Format incorrect pour la ligne : '{line}'. "
            "Format attendu : RQ1. Texte de la question"
        )

    identifier = match.group(1).upper()

    if not re.fullmatch(r"RQ[0-9]+", identifier):
        raise ValueError(
            f"Identifiant incorrect : '{identifier}'. "
            "Les identifiants attendus sont RQ1, RQ2 et RQ3."
        )

    return {
        "identifier": identifier,
        "question": match.group(2).strip(),
    }


def validate_identifiers(records: list[dict]) -> None:
    """Vérifie les identifiants RQ1, RQ2 et RQ3 dans cet ordre."""

    expected = ["RQ1", "RQ2", "RQ3"]

    actual = [
        record["identifier"]
        for record in records
    ]

    if actual != expected:
        raise ValueError(
            f"Identifiants incorrects : {actual}. "
            f"Identifiants attendus : {expected}."
        )


def validate_no_duplicates(records: list[dict]) -> None:
    """Détecte les questions dupliquées."""

    normalized_questions = [
        " ".join(record["question"].casefold().split())
        for record in records
    ]

    if len(normalized_questions) != len(set(normalized_questions)):
        raise ValueError("Des questions dupliquées ont été détectées.")


def validate_free_text(text: str) -> list[dict]:
    """
    Valide le texte brut.

    1. Vérifie le nombre de lignes.
    2. Vérifie le format de chaque ligne.
    3. Vérifie les identifiants.
    4. Détecte les doublons.
    """

    lines = extract_non_empty_lines(text)

    # Vérifier d'abord les identifiants si trois lignes sont présentes.
    # Cela permet de détecter précisément R2 au lieu de signaler
    # uniquement une erreur de nombre de lignes.
    if len(lines) == 3:
        records = [
            parse_rq_line(line)
            for line in lines
        ]

        validate_identifiers(records)
        validate_no_duplicates(records)

        return records

    raise ValueError(
        f"Trois questions sont attendues, mais {len(lines)} "
        "ligne(s) non vide(s) ont été détectées."
    )


def validate_questions(records: list[dict]) -> list[ResearchQuestion]:
    """Valide les questions avec le modèle Pydantic."""

    return [
        ResearchQuestion.model_validate(record)
        for record in records
    ]
