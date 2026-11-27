
from slrresearch.agents.screening_agent import ScreeningAgent
from slrresearch.schemas.screening import (
    ScreeningCriteria,
    ScreeningDecision,
    ScreeningIndicators,
    SemanticScreeningResult,
    LLMScreeningDecision,
)
from slrresearch.core.react.contracts import PaperRecord


class FakeLLMAgent:
    def analyze(self, paper, criteria):
        return LLMScreeningDecision(
            paper_id=paper.id,
            decision="include",
            confidence=0.90,
            reasons=["L'article répond aux critères."],
        )


class FakeSemanticService:
    def analyze_paper(self, paper, criteria):
        return SemanticScreeningResult(
            paper_id=paper.id,
            inclusion_scores=[],
            exclusion_scores=[],
        )


def fake_deterministic_screening(
    paper,
    include_terms,
    exclude_terms,
):
    return ScreeningDecision(
        paper_id=paper.id,
        decision="include",
        confidence=0.90,
        reasons=["Correspondance avec les critères d'inclusion."],
        indicators=ScreeningIndicators(
            inclusion_matches=["machine learning"],
            exclusion_matches=[],
            information_sufficient=True,
            conflict=False,
        ),
    )


def test_screening_agent_includes_paper(monkeypatch):
    import slrresearch.agents.screening_agent as screening_module

    monkeypatch.setattr(
        screening_module,
        "screen_paper_deterministically",
        fake_deterministic_screening,
    )

    agent = ScreeningAgent(
        llm_agent=FakeLLMAgent(),
        semantic_service=FakeSemanticService(),
    )

    paper = PaperRecord(
        id="paper_001",
        title="Machine Learning for Healthcare",
        abstract="A study about machine learning applications.",
        source="OpenAlex",
    )

    criteria = ScreeningCriteria(
        inclusion_criteria=["Studies about machine learning"],
        exclusion_criteria=["Studies unrelated to healthcare"],
        inclusion_terms=["machine learning"],
        exclusion_terms=["unrelated"],
    )

    result = agent.run(
        papers=[paper],
        criteria=criteria,
    )

    assert result.deduplication.total_input == 1
    assert result.deduplication.total_unique == 1

    assert len(result.title_abstract_decisions) == 1
    assert result.title_abstract_decisions[0].final_decision == "include"

    assert len(result.selected_papers) == 1
    assert result.selected_papers[0].id == "paper_001"

    assert result.human_review_queue == []

def test_screening_agent_excludes_paper(monkeypatch):
    import slrresearch.agents.screening_agent as screening_module

    monkeypatch.setattr(
        screening_module,
        "screen_paper_deterministically",
        lambda paper, include_terms, exclude_terms: ScreeningDecision(
            paper_id=paper.id,
            decision="exclude",
            confidence=0.90,
            reasons=["Indicateur d'exclusion détecté."],
            indicators=ScreeningIndicators(
                inclusion_matches=[],
                exclusion_matches=["unrelated"],
                information_sufficient=True,
                conflict=False,
            ),
        ),
    )

    class ExcludingLLM:
        def analyze(self, paper, criteria):
            return LLMScreeningDecision(
                paper_id=paper.id,
                decision="exclude",
                confidence=0.90,
                reasons=["L'article ne respecte pas les critères."],
            )

    agent = ScreeningAgent(
        llm_agent=ExcludingLLM(),
        semantic_service=FakeSemanticService(),
    )

    paper = PaperRecord(
        id="paper_002",
        title="Unrelated Study",
        source="Crossref",
    )

    criteria = ScreeningCriteria(
        inclusion_criteria=["Studies about machine learning"],
        exclusion_criteria=["Unrelated studies"],
        inclusion_terms=["machine learning"],
        exclusion_terms=["unrelated"],
    )

    result = agent.run([paper], criteria)

    assert result.title_abstract_decisions[0].final_decision == "exclude"
    assert result.selected_papers == []
    assert result.human_review_queue == []


def test_screening_agent_sends_uncertain_paper_to_human_review(
    monkeypatch,
):
    import slrresearch.agents.screening_agent as screening_module

    monkeypatch.setattr(
        screening_module,
        "screen_paper_deterministically",
        lambda paper, include_terms, exclude_terms: ScreeningDecision(
            paper_id=paper.id,
            decision="include",
            confidence=0.70,
            reasons=["Signal d'inclusion détecté."],
            indicators=ScreeningIndicators(
                inclusion_matches=["machine learning"],
                exclusion_matches=[],
                information_sufficient=False,
                conflict=False,
            ),
        ),
    )

    class UncertainLLM:
        def analyze(self, paper, criteria):
            return LLMScreeningDecision(
                paper_id=paper.id,
                decision="uncertain",
                confidence=0.40,
                reasons=["Informations insuffisantes."],
            )

    agent = ScreeningAgent(
        llm_agent=UncertainLLM(),
        semantic_service=FakeSemanticService(),
    )

    paper = PaperRecord(
        id="paper_003",
        title="Machine Learning Study",
        source="OpenAlex",
    )

    criteria = ScreeningCriteria(
        inclusion_criteria=["Studies about machine learning"],
        exclusion_criteria=["Studies unrelated to the topic"],
        inclusion_terms=["machine learning"],
        exclusion_terms=["unrelated"],
    )

    result = agent.run([paper], criteria)

    assert result.title_abstract_decisions[0].final_decision == "uncertain"
    assert result.title_abstract_decisions[0].needs_human_review is True
    assert result.human_review_queue == ["paper_003"]
    assert result.selected_papers == []


def test_screening_agent_deduplicates_before_screening(monkeypatch):
    import slrresearch.agents.screening_agent as screening_module

    analyzed_papers = []

    def fake_screening(paper, include_terms, exclude_terms):
        analyzed_papers.append(paper.id)

        return ScreeningDecision(
            paper_id=paper.id,
            decision="include",
            confidence=0.90,
            reasons=["Correspondance détectée."],
            indicators=ScreeningIndicators(
                inclusion_matches=["machine learning"],
                exclusion_matches=[],
                information_sufficient=True,
                conflict=False,
            ),
        )

    monkeypatch.setattr(
        screening_module,
        "screen_paper_deterministically",
        fake_screening,
    )

    agent = ScreeningAgent(
        llm_agent=FakeLLMAgent(),
        semantic_service=FakeSemanticService(),
    )

    papers = [
        PaperRecord(
            id="paper_004",
            title="Machine Learning in Healthcare",
            abstract="",
            doi="10.1234/example",
            source="OpenAlex",
        ),
        PaperRecord(
            id="paper_005",
            title="Another title",
            abstract="A detailed abstract about machine learning.",
            doi="https://doi.org/10.1234/example",
            source="Crossref",
            url="https://example.org/paper",
            open_access=True,
        ),
    ]

    criteria = ScreeningCriteria(
        inclusion_criteria=["Studies about machine learning"],
        exclusion_criteria=["Studies unrelated to the topic"],
        inclusion_terms=["machine learning"],
        exclusion_terms=["unrelated"],
    )

    result = agent.run(papers, criteria)

    assert result.deduplication.total_input == 2
    assert result.deduplication.total_unique == 1
    assert len(result.deduplication.duplicate_groups) == 1
    assert analyzed_papers == ["paper_005"]
    assert len(result.title_abstract_decisions) == 1
    assert result.title_abstract_decisions[0].paper_id == "paper_005"
