
import json


def build_technology_extraction_prompt(questions: list) -> str:
    questions_data = [
        {
            "identifier": question.identifier,
            "question": question.question
        }
        for question in questions
    ]

    questions_json = json.dumps(
        questions_data,
        ensure_ascii=False,
        indent=2
    )

    return f"""
Tu es un expert en Systematic Literature Review (SLR)
et en méthodologie de recherche scientifique.

Ta mission est d'analyser les Research Questions approuvées
par le chercheur et d'en extraire les concepts nécessaires
pour construire des requêtes de recherche bibliographique.

Research Questions :
{questions_json}

Identifie les trois catégories suivantes :

1. technologies :
Les technologies, méthodes, modèles ou approches techniques
étudiés dans le sujet.
Exemples : Artificial Intelligence, Large Language Models,
Machine Learning, CNN, Blockchain.

2. domain_concepts :
Les concepts qui représentent le domaine scientifique
ou le contexte de la recherche.
Exemples : Education, Healthcare, Agriculture,
Higher Education, Medical Imaging.

3. research_tasks :
Les activités, problèmes ou phénomènes étudiés dans le domaine.
Exemples : Personalized Learning, Disease Detection,
Image Classification, Student Performance Prediction.

Instructions importantes :
- Analyse toutes les Research Questions ensemble.
- Extrais uniquement les concepts pertinents pour le sujet.
- Ne confonds pas les tâches internes d'une SLR
  (screening, study selection, duplicate removal)
  avec les research_tasks du sujet scientifique.
- Évite les termes trop généraux et les doublons.
- Regroupe les synonymes ou expressions équivalentes
  lorsque cela est pertinent.
- N'invente aucun concept qui n'est pas justifié
  par les Research Questions.
- Si une catégorie ne contient aucun concept pertinent,
  retourne une liste vide.
- Les concepts doivent être en anglais pour faciliter
  la recherche dans les bases scientifiques.

Retourne uniquement un objet JSON respectant exactement
cette structure :

{{
    "technologies": [
        "Large Language Models",
        "Artificial Intelligence"
    ],
    "domain_concepts": [
        "Education",
        "Higher Education"
    ],
    "research_tasks": [
        "Personalized Learning",
        "Student Performance Prediction"
    ]
}}

Ne donne aucune explication avant ou après le JSON.
"""
