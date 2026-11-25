
"""
Prompts utilisés par le ResearchQuestionAgent.

Ce module centralise les prompts du TD01 et du TD02 :
- Zero-shot : génération des Research Questions.
- Few-shot : génération avec exemples.
- Repair : correction du format des questions.

Les prompts sont adaptés aux entrées du projet :
sujet, objectif et contexte facultatif.
"""


def _validate_inputs(
    topic: str,
    objective: str,
    context: str = "",
) -> tuple[str, str, str]:
    """Nettoie et vérifie les entrées utilisateur."""

    clean_topic = topic.strip()
    clean_objective = objective.strip()
    clean_context = context.strip()

    if not clean_topic:
        raise ValueError("Le sujet ne doit pas être vide")

    if not clean_objective:
        raise ValueError("L'objectif ne doit pas être vide")

    return clean_topic, clean_objective, clean_context


def build_system_prompt() -> str:
    """
    TD01 - Définit le rôle et les règles stables du modèle.
    """

    return (
        "Tu es un assistant méthodologique spécialisé dans les revues "
        "systématiques de la littérature (SLR). "
        "Reste dans le périmètre du sujet, de l'objectif et du contexte "
        "fournis. "
        "N'invente ni référence ni résultat scientifique. "
        "Réponds en français."
    )


def build_user_prompt(
    topic: str,
    objective: str,
    context: str = "",
) -> str:
    """
    TD01 - Construit un prompt Zero-shot à partir des entrées utilisateur.
    """

    clean_topic, clean_objective, clean_context = _validate_inputs(
        topic, objective, context
    )

    context_section = (
        clean_context
        if clean_context
        else "Aucun contexte complémentaire fourni."
    )

    return f"""[SUJET]
{clean_topic}

[OBJECTIF]
{clean_objective}

[CONTEXTE]
{context_section}

[TACHE]
Générer exactement trois questions de recherche
(Research Questions) pour cette revue systématique
de la littérature.

[CONTRAINTES]
- Les questions doivent répondre à l'objectif de la revue.
- Elles doivent être ouvertes, claires et précises.
- Elles doivent être distinctes et complémentaires.
- Elles doivent rester dans le périmètre du sujet et du contexte.
- Ne pas inventer de références ou de résultats scientifiques.
- Ne pas répondre aux questions.

[FORMAT DE SORTIE]
Retourner exactement trois lignes :
RQ1. ...
RQ2. ...
RQ3. ...

Ne produire aucune introduction ni conclusion.
Ne pas utiliser de Markdown ni de JSON.
"""


def build_zero_shot_prompt(
    topic: str,
    objective: str,
    context: str = "",
) -> str:
    """Compatibilité TD01 : retourne le prompt utilisateur Zero-shot."""

    return build_user_prompt(topic, objective, context)


def build_few_shot_prompt(
    topic: str,
    objective: str,
    context: str = "",
) -> str:
    """
    TD02 - Construit un prompt Few-shot avec deux exemples.

    Les exemples illustrent le format et la complémentarité
    des questions. Le sujet courant reste prioritaire.
    """

    clean_topic, clean_objective, clean_context = _validate_inputs(
        topic, objective, context
    )

    context_section = (
        clean_context
        if clean_context
        else "Aucun contexte complémentaire fourni."
    )

    return f"""Tu es un assistant méthodologique spécialisé
dans les revues systématiques de la littérature (SLR).

Ta tâche est de générer exactement trois questions de recherche.

Voici deux exemples :

Exemple 1 :
Sujet : IA et éducation
Objectif : Étudier l'utilisation de l'IA dans l'éducation.

RQ1. Comment l'IA influence-t-elle la personnalisation pédagogique ?
RQ2. Quels risques l'IA introduit-elle dans l'évaluation ?
RQ3. Quel contrôle humain doit-il être conservé ?

Exemple 2 :
Sujet : DevOps et qualité logicielle
Objectif : Étudier l'influence de DevOps sur la qualité logicielle.

RQ1. Comment DevOps influence-t-il la fréquence des déploiements ?
RQ2. Quels facteurs réduisent-ils les défauts en production ?
RQ3. Quelles métriques permettent-elles d'évaluer cette amélioration ?

[SUJET ACTUEL]
{clean_topic}

[OBJECTIF]
{clean_objective}

[CONTEXTE]
{context_section}

[CONTRAINTES]
- Générer exactement trois questions.
- Respecter le sujet, l'objectif et le contexte.
- Produire des questions ouvertes et distinctes.
- Chaque question doit contenir au moins 15 caractères.
- Utiliser les identifiants RQ1, RQ2 et RQ3 dans cet ordre.
- Ne pas ajouter d'introduction ni de conclusion.
- Ne pas utiliser de Markdown ni de JSON.

[FORMAT ATTENDU]
RQ1. ...
RQ2. ...
RQ3. ...
"""


def build_repair_prompt(text: str, error: str) -> str:
    """
    TD02 - Demande une réparation ciblée du format des RQs.

    Le sens scientifique des questions doit être préservé.
    """

    if not text.strip():
        raise ValueError("Le texte à réparer ne doit pas être vide")

    return f"""Tu es un assistant méthodologique spécialisé
dans les revues systématiques de la littérature (SLR).

Ta tâche consiste uniquement à corriger le format
des questions de recherche ci-dessous.

[ERREUR DE VALIDATION]
{error}

[TEXTE À CORRIGER]
{text}

[CONTRAINTES]
- Corriger uniquement les problèmes de format.
- Préserver le sens scientifique de chaque question.
- Ne pas inventer de nouvelles questions.
- Retourner exactement trois questions.
- Utiliser RQ1, RQ2 et RQ3 dans cet ordre.
- Chaque question doit contenir au moins 15 caractères.
- Ne pas ajouter d'introduction ni de conclusion.
- Ne pas utiliser de Markdown ni de JSON.

[FORMAT ATTENDU]
RQ1. ...
RQ2. ...
RQ3. ...
"""
