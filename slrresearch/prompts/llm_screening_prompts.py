
import json


def build_llm_screening_prompt(paper, criteria):
    """
    Construit le prompt d'analyse d'un article
    selon les critères approuvés par le chercheur.
    """

    inclusion_criteria = "\n".join(
        f"{i + 1}. {criterion}"
        for i, criterion in enumerate(criteria.inclusion_criteria)
    )

    exclusion_criteria = "\n".join(
        f"{i + 1}. {criterion}"
        for i, criterion in enumerate(criteria.exclusion_criteria)
    )

    all_criteria = (
        criteria.inclusion_criteria
        + criteria.exclusion_criteria
    )

    total_criteria = len(all_criteria)

    expected_assessments = ",\n".join(
        f'''        {{
            "criterion": {json.dumps(criterion, ensure_ascii=False)},
            "status": "uncertain",
            "evidence": "",
            "explanation": ""
        }}'''
        for criterion in all_criteria
    )

    return f"""
Tu es un assistant spécialisé dans le screening
des articles scientifiques pour une revue systématique
de littérature (SLR).

Ta mission est d'analyser un article scientifique
à partir de son titre et de son résumé, en respectant
strictement les critères approuvés par le chercheur.

ARTICLE :

ID : {paper.id}

Titre :
{paper.title}

Résumé :
{paper.abstract or "Résumé non disponible."}

CRITÈRES D'INCLUSION :
{inclusion_criteria}

CRITÈRES D'EXCLUSION :
{exclusion_criteria}

INSTRUCTIONS OBLIGATOIRES :

1. Évalue individuellement TOUS les critères d'inclusion
   et TOUS les critères d'exclusion.

2. Tu dois retourner exactement {total_criteria}
   objets dans criterion_assessments.

3. Chaque critère doit apparaître UNE SEULE FOIS,
   avec exactement le même texte que celui fourni.

4. Respecte impérativement cet ordre :
   - D'abord tous les critères d'inclusion.
   - Ensuite tous les critères d'exclusion.

5. N'ignore aucun critère, même s'il semble évident
   ou sans rapport avec l'article.

6. Pour chaque critère, attribue un statut :
   - satisfied : le contenu confirme le critère.
   - not_satisfied : le contenu montre que le critère
     n'est pas respecté.
   - uncertain : les informations sont insuffisantes
     ou ambiguës.

7. Fournis une preuve textuelle exacte tirée du titre
   ou du résumé. Ne fabrique jamais de citation.

8. Explique brièvement chaque évaluation.

9. Donne une décision globale :
   - include : les critères d'inclusion sont satisfaits
     et aucun critère d'exclusion n'est satisfait.
   - exclude : au moins un critère d'exclusion est satisfait
     ou un critère d'inclusion est clairement non satisfait.
   - uncertain : les informations ne permettent pas
     de prendre une décision fiable.

10. Si des informations importantes sont absentes,
    ne les invente pas. Utilise uncertain.

11. La confiance doit refléter ton niveau de certitude,
    sans prétendre être une probabilité calibrée.

12. Vérifie avant de répondre que le nombre d'évaluations
    est exactement {total_criteria}.

RÈGLES STRICTES POUR LES PREUVES :

13. Le champ "evidence" de chaque évaluation doit contenir
    uniquement un extrait copié exactement depuis le titre
    ou le résumé de l'article.

14. Respecte exactement les mots, l'ordre des mots,
    la ponctuation et la formulation de l'extrait original.

15. Ne reformule jamais le contenu de l'article dans
    le champ "evidence".

16. N'écris jamais une explication ou une interprétation
    dans le champ "evidence".

    Exemples de formulations interdites :
    - "Le titre ne mentionne pas..."
    - "Le résumé ne contient pas..."
    - "L'article ne fournit aucune information sur..."

17. Si aucune preuve textuelle directe ne permet
    de justifier l'évaluation, retourne une chaîne vide :
    "evidence": ""

18. Le champ "explanation" est différent :
    il doit contenir ton interprétation et expliquer
    pourquoi le critère est satisfied, not_satisfied
    ou uncertain.

19. Le champ global "evidence" doit également contenir
    uniquement des extraits exacts du titre ou du résumé.
    Ne mets aucune reformulation dans ce champ.

20. N'utilise aucune information extérieure au titre
    et au résumé pour justifier tes évaluations.

RÈGLES POUR LA CONFIANCE :

21. Le champ "confidence" représente ton niveau de confiance
    dans la décision globale.

22. Retourne obligatoirement une valeur numérique
    comprise entre 0.0 et 1.0.

23. Choisis cette valeur en fonction des éléments suivants :

    - 0.90 à 1.00 : décision très claire, preuves directes
      et aucune ambiguïté importante.

    - 0.75 à 0.89 : décision bien justifiée avec
      quelques petites incertitudes.

    - 0.50 à 0.74 : décision modérément justifiée,
      avec des informations incomplètes.

    - 0.00 à 0.49 : décision très incertaine,
      avec des preuves insuffisantes ou contradictoires.

24. La confiance doit être cohérente avec la décision :
    - Une décision "uncertain" doit généralement avoir
      une confiance plus faible.
    - Une décision clairement justifiée peut avoir
      une confiance élevée.

25. Ne retourne pas systématiquement la même valeur.
    Évalue réellement le niveau de certitude de chaque article.

26. Ne copie pas la valeur illustrative du JSON ci-dessous.
    Choisis ta propre valeur de confidence pour cet article.

FORMAT DE SORTIE :

Retourne uniquement un objet JSON valide, sans Markdown,
avec exactement cette structure :

{{
    "paper_id": {json.dumps(paper.id)},
    "decision": "include",
    "confidence": 0.75,
    "reasons": [
        "Explication de la décision"
    ],
    "evidence": "Extrait exact du titre ou du résumé",
    "needs_human_review": false,
    "criterion_assessments": [
{expected_assessments}
    ]
}}

IMPORTANT :
- Le JSON doit être valide.
- Ne retourne aucun texte avant ou après le JSON.
- Respecte exactement les noms des champs.
- Ne modifie pas les textes des critères.
- Retourne exactement {total_criteria} évaluations.
- La valeur de confidence doit être choisie selon
  l'article analysé et non copiée depuis cet exemple.
"""
