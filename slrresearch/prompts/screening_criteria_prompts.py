
def build_screening_criteria_prompt(
    objective: str,
    approved_questions: list,
) -> str:
    """
    Construit le prompt pour générer les critères
    scientifiques et les indicateurs lexicaux d'une SLR.
    """

    if not objective or not objective.strip():
        raise ValueError("L'objectif de la SLR est obligatoire.")

    if not approved_questions:
        raise ValueError(
            "Au moins une Research Question approuvée est nécessaire."
        )

    questions = []

    for question in approved_questions:
        if hasattr(question, "identifier") and hasattr(question, "question"):
            questions.append(
                f"{question.identifier}: {question.question}"
            )
        else:
            questions.append(str(question))

    questions_text = "\n".join(questions)

    return f"""
You are an expert in Systematic Literature Reviews (SLR) methodology.

Your task is to generate scientifically justified inclusion and
exclusion criteria, as well as lexical indicators for a systematic
literature review.

SLR OBJECTIVE:
{objective}

APPROVED RESEARCH QUESTIONS:
{questions_text}

INSTRUCTIONS:

1. Analyze the objective and all approved research questions together.

2. Generate specific inclusion criteria defining which studies are
   relevant to this SLR.

3. Generate specific exclusion criteria defining which studies
   fall outside its scope.

4. Ensure that all criteria are consistent with the objective
   and approved research questions.

5. Avoid redundant, contradictory, vague, or overly restrictive criteria.

6. Do not invent publication dates, languages, geographical limits,
   study types, or other restrictions that were not specified.

7. Each criterion must express one clear and understandable condition.
   Write criteria as complete scientific statements, not keywords.

8. Generate lexical indicators associated with the inclusion criteria.
   These indicators will be used by a deterministic screening component
   to detect relevant expressions in article titles and abstracts.

9. Generate lexical indicators associated with the exclusion criteria
   using the same principle.

10. Lexical indicators must:
    - Be short words or expressions.
    - Represent concepts explicitly related to the corresponding criteria.
    - Include relevant technical terms, synonyms and common variants.
    - Be specific enough to reduce false matches.
    - Be written in the language or languages relevant to the research topic.
    - Avoid generic words that provide little information.

11. Do not invent keywords, technologies, concepts or synonyms that
    are not justified by the objective and research questions.

12. Do not assume that the absence of a lexical indicator proves
    that an article is irrelevant. Lexical indicators are preliminary
    signals, not final screening decisions.

13. Criteria and lexical indicators must remain consistent:
    each lexical indicator must support at least one corresponding
    inclusion or exclusion criterion.

14. Generate criteria that can be applied during title/abstract
    screening and, where appropriate, full-text screening.

15. Do not make screening decisions about individual articles.

Return ONLY a valid JSON object with this exact structure:

{{
    "inclusion_criteria": [
        "First complete inclusion criterion",
        "Second complete inclusion criterion"
    ],
    "exclusion_criteria": [
        "First complete exclusion criterion",
        "Second complete exclusion criterion"
    ],
    "inclusion_terms": [
        "Relevant technical expression",
        "Relevant synonym"
    ],
    "exclusion_terms": [
        "Relevant exclusion expression",
        "Relevant synonym"
    ]
}}
"""
