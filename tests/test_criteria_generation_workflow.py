
import pytest
from pydantic import ValidationError

from slrresearch.schemas.screening import ScreeningCriteria
from slrresearch.workflows.criteria_generation_workflow import (
    CriteriaGenerationWorkflow,
)


@pytest.fixture
def sample_criteria():
    return ScreeningCriteria(
        inclusion_criteria=[
            "Studies related to machine learning in healthcare."
        ],
        exclusion_criteria=[
            "Studies unrelated to healthcare."
        ],
    )


@pytest.fixture
def sample_review(sample_criteria):
    return CriteriaGenerationWorkflow.start_review(sample_criteria)


def test_start_review_creates_pending_session(sample_criteria):
    review = CriteriaGenerationWorkflow.start_review(sample_criteria)

    assert review.status == "pending"
    assert review.criteria == sample_criteria
    assert review.original_criteria == sample_criteria


def test_edit_criteria(sample_review):
    review = CriteriaGenerationWorkflow.edit_criteria(
        review=sample_review,
        inclusion_criteria=[
            "Studies applying deep learning in medical diagnosis."
        ],
        exclusion_criteria=[
            "Studies without a medical application."
        ],
    )

    assert review.status == "pending"
    assert review.criteria.inclusion_criteria == [
        "Studies applying deep learning in medical diagnosis."
    ]


def test_edit_does_not_modify_original_criteria(sample_review):
    original_inclusion = list(
        sample_review.original_criteria.inclusion_criteria
    )

    CriteriaGenerationWorkflow.edit_criteria(
        review=sample_review,
        inclusion_criteria=["New inclusion criterion."],
        exclusion_criteria=["New exclusion criterion."],
    )

    assert (
        sample_review.original_criteria.inclusion_criteria
        == original_inclusion
    )


def test_edit_rejects_empty_criteria(sample_review):
    with pytest.raises(ValidationError):
        CriteriaGenerationWorkflow.edit_criteria(
            review=sample_review,
            inclusion_criteria=[],
            exclusion_criteria=["Studies unrelated to healthcare."],
        )


def test_approve_criteria(sample_review):
    review = CriteriaGenerationWorkflow.approve(sample_review)

    assert review.status == "approved"
    assert review.rejection_reason is None


def test_reject_criteria(sample_review):
    review = CriteriaGenerationWorkflow.reject(
        sample_review,
        reason="The criteria do not match the research objective.",
    )

    assert review.status == "rejected"
    assert (
        review.rejection_reason
        == "The criteria do not match the research objective."
    )


def test_get_approved_criteria(sample_review):
    CriteriaGenerationWorkflow.approve(sample_review)

    criteria = CriteriaGenerationWorkflow.get_approved_criteria(
        sample_review
    )

    assert isinstance(criteria, ScreeningCriteria)
    assert criteria == sample_review.criteria


def test_cannot_get_unapproved_criteria(sample_review):
    with pytest.raises(ValueError):
        CriteriaGenerationWorkflow.get_approved_criteria(sample_review)


def test_cannot_edit_approved_criteria(sample_review):
    CriteriaGenerationWorkflow.approve(sample_review)

    with pytest.raises(ValueError):
        CriteriaGenerationWorkflow.edit_criteria(
            review=sample_review,
            inclusion_criteria=["New criterion."],
            exclusion_criteria=["Another criterion."],
        )


def test_cannot_approve_rejected_criteria(sample_review):
    CriteriaGenerationWorkflow.reject(
        sample_review,
        reason="Incorrect criteria.",
    )

    with pytest.raises(ValueError):
        CriteriaGenerationWorkflow.approve(sample_review)
