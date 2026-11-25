
"""
Test d'intégration du ResearchQuestionAgent avec Ollama ou Groq.
"""

from slrresearch.config import Settings, build_model
from slrresearch.agents.research_question_agent import ResearchQuestionAgent


def test_research_question_agent_generation():
    # 1. Charger la configuration
    settings = Settings()

    # 2. Construire le modèle LLM
    model = build_model(settings)

    # 3. Créer le ResearchQuestionAgent
    agent = ResearchQuestionAgent(
        model=model,
        provider=settings.provider,
    )

    # 4. Définir le sujet, l'objectif et le contexte
    topic = (
        "Utilisation des Large Language Models "
        "dans le screening des revues systématiques"
    )

    objective = (
        "Étudier comment les LLM peuvent automatiser "
        "la sélection des articles scientifiques."
    )

    context = (
        "Domaine du génie logiciel. "
        "L'étude porte sur le screening des titres et résumés."
    )

    # 5. Exécuter l'agent
    result = agent.run(
        topic=topic,
        objective=objective,
        context=context,
    )

    # 6. Afficher les résultats
    print("\n========== RÉSULTAT DU RESEARCH QUESTION AGENT ==========")
    print("Statut :", result.status)
    print("Nombre de tentatives de correction :", result.repair_attempts)
    print("\nQuestions générées :")
    print(result.text)

    if result.error:
        print("\nErreur :", result.error)

    # 7. Vérifier le résultat
    assert result.status in {"accepted", "repaired"}
    assert len(result.questions) == 3

    identifiers = [
        question.identifier
        for question in result.questions
    ]

    assert identifiers == ["RQ1", "RQ2", "RQ3"]

    print("\nTest réussi !")


if __name__ == "__main__":
    test_research_question_agent_generation()
