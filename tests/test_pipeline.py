from unittest.mock import Mock

import pytest

from src.domain import ReviewStatus
from src.exceptions import (
    HumanReviewRequiredError,
    RejectedContentError,
    RepeatedReviewError
)
from src.pipeline.pipeline import ReviewPipeline, log_processing_time


def raw(text="عالی", review_id="r"):
    return {
        "product_category": "home_appliances",
        "review_id": review_id,
        "user_id": "u",
        "product_id": "p",
        "purchase_source": "not_purchased",
        "overall_satisfaction": 5,
        "review_text": text,
    }


def make_pipeline(validator=None, labeler=None):
    factory = Mock()
    review = Mock()
    review.status = ReviewStatus.UNDEFINED
    review.labels = set()
    review.user_id = "u"
    review.review_id = "r"
    review.purchase_source = "not_purchased"
    review.product_category = "home_appliances"
    factory.return_value = review
    return ReviewPipeline(factory, validator or Mock(), labeler or Mock()), factory, review


def test_auto_approved_and_stats():
    pipeline, factory, review = make_pipeline()
    result = pipeline.process(raw())
    assert result is review
    assert review.status == ReviewStatus.AUTO_APPROVED
    factory.assert_called_once_with("home_appliances", raw())


def test_human_review_from_validator():
    validator = Mock()
    validator.validate.side_effect = HumanReviewRequiredError("flag")
    pipeline, _, _ = make_pipeline(validator=validator)
    result = pipeline.process(raw(review_id='hrfv'))
    assert result.status == ReviewStatus.NEEDS_HUMAN_REVIEW


def test_rejected_from_validator_is_recorded():
    validator = Mock()
    validator.validate.side_effect = RejectedContentError("bad")
    pipeline, _, _ = make_pipeline(validator=validator)
    result = pipeline.process(raw())
    assert result.status == ReviewStatus.REJECTED


def test_human_review_from_labeler():
    labeler = Mock()
    labeler.label.side_effect = HumanReviewRequiredError("flag")
    pipeline, _, review = make_pipeline(labeler=labeler)
    result = pipeline.process(raw())
    assert result.status == ReviewStatus.NEEDS_HUMAN_REVIEW


def test_batch_process_groups_and_logs(capsys):
    pipeline, _, review = make_pipeline()
    result = pipeline.batch_process([raw(), raw()])
    assert result[ReviewStatus.AUTO_APPROVED] == [review, review]
    assert "batch_process completed in" in capsys.readouterr().out


def test_process_repeat_error():
    pipeline, _, _ = make_pipeline()
    pipeline.process(raw())
    pipeline._repeated_review_error = True
    with pytest.raises(RepeatedReviewError):
        pipeline.process(raw())


def test_decorator_preserves_name_and_result():
    @log_processing_time
    def sample(value):
        return value + 1
    assert sample.__name__ == "sample"
    assert sample(2) == 3
