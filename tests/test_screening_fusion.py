
import pytest

from slrresearch.schemas.screening import (
    ScreeningDecision,
    ScreeningIndicators,
    SemanticScreeningResult,
    CriterionSimilarity,
    LLMScreeningDecision,
)

from slrresearch.services.screening.screening_fusion import (
    SemanticFusionConfig,
    fuse_screening_results,
)


def create_deterministic(
    decision="include",
    information_sufficient=True,
    conflict=False,
    inclusion_matches=None,
    exclusion_matches=None,
):
    return ScreeningDecision(
        paper_id="paper_001",
        decision=decision,
        confidence=0.90,
        reasons=["Analyse déterministe"],
        indicators=ScreeningIndicators(
            inclusion_matches=inclusion_matches or [],
            exclusion_matches=exclusion_matches or [],
            information_sufficient=information_sufficient,
            conflict=conflict,
        ),
    )


def create_semantic(
    inclusion_scores=None,
    exclusion_scores=None,
):
    return SemanticScreeningResult(
        paper_id="paper_001",
        inclusion_scores=inclusion_scores or [],
        exclusion_scores=exclusion_scores or [],
    )


def create_llm(decision="include"):
    return LLMScreeningDecision(
        paper_id="paper_001",
        decision=decision,
        confidence=0.90,
        reasons=["Analyse LLM"],
    )


def test_fusion_include_when_analyses_agree():
    result = fuse_screening_results(
        deterministic=create_deterministic(),
        semantic=create_semantic(),
        llm=create_llm(),
    )

    assert result.final_decision == "include"
    assert result.agreement is True
    assert result.needs_human_review is False


def test_fusion_exclude_when_analyses_agree():
    result = fuse_screening_results(
        deterministic=create_deterministic(
            decision="exclude",
            exclusion_matches=["Article hors sujet"],
        ),
        semantic=create_semantic(),
        llm=create_llm("exclude"),
    )

    assert result.final_decision == "exclude"
    assert result.needs_human_review is False


def test_fusion_uncertain_when_deterministic_and_llm_disagree():
    result = fuse_screening_results(
        deterministic=create_deterministic("include"),
        semantic=create_semantic(),
        llm=create_llm("exclude"),
    )

    assert result.final_decision == "uncertain"
    assert result.agreement is False
    assert result.needs_human_review is True
    assert result.escalation_reason is not None


def test_fusion_uncertain_when_llm_is_uncertain():
    result = fuse_screening_results(
        deterministic=create_deterministic("uncertain"),
        semantic=create_semantic(),
        llm=create_llm("uncertain"),
    )

    assert result.final_decision == "uncertain"
    assert result.needs_human_review is True


def test_fusion_uncertain_when_information_is_insufficient():
    result = fuse_screening_results(
        deterministic=create_deterministic(
            information_sufficient=False
        ),
        semantic=create_semantic(),
        llm=create_llm("include"),
    )

    assert result.final_decision == "uncertain"
    assert result.needs_human_review is True


def test_fusion_uncertain_when_deterministic_signals_conflict():
    result = fuse_screening_results(
        deterministic=create_deterministic(
            conflict=True,
            inclusion_matches=["Deep Learning"],
            exclusion_matches=["Méthode hors sujet"],
        ),
        semantic=create_semantic(),
        llm=create_llm("include"),
    )

    assert result.final_decision == "uncertain"
    assert result.needs_human_review is True


def test_fusion_uncertain_when_semantic_signal_contradicts_llm():
    semantic = create_semantic(
        inclusion_scores=[
            CriterionSimilarity(
                criterion="Utilise le Deep Learning",
                similarity=0.30,
            )
        ],
        exclusion_scores=[
            CriterionSimilarity(
                criterion="Article hors sujet",
                similarity=0.90,
            )
        ],
    )

    config = SemanticFusionConfig(
        inclusion_threshold=0.70,
        exclusion_threshold=0.70,
    )

    result = fuse_screening_results(
        deterministic=create_deterministic("include"),
        semantic=semantic,
        llm=create_llm("include"),
        config=config,
    )

    assert result.final_decision == "uncertain"
    assert result.needs_human_review is True


def test_fusion_rejects_different_paper_ids():
    semantic = SemanticScreeningResult(
        paper_id="paper_002",
        inclusion_scores=[],
        exclusion_scores=[],
    )

    with pytest.raises(ValueError):
        fuse_screening_results(
            deterministic=create_deterministic(),
            semantic=semantic,
            llm=create_llm(),
        )


def test_semantic_config_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        SemanticFusionConfig(
            inclusion_threshold=1.5,
            exclusion_threshold=0.70,
        )


def test_semantic_config_requires_both_thresholds():
    with pytest.raises(ValueError):
        SemanticFusionConfig(
            inclusion_threshold=0.70,
        )
