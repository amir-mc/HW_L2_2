import pytest

from src.domain import PurchaseSource
from src.domain import labels, ReviewStatus, PurchaseSource
from src.models import HomeApplianceReview
from src.services.labelers import LLMLabeler, RuleBasedLabeler
from src.user_stats import _Stats, stats


def make_review(source="our_system", score=5, user="u", status="auto_approved"):
    review = HomeApplianceReview(
        review_id=f"r-{user}-{score}",
        user_id=user,
        product_id="p",
        purchase_source=source,
        overall_satisfaction=score,
        review_text="ok",
    )
    review.status = ReviewStatus(status)
    return review


def test_first_repeat_and_expert_labels():
    labeler = RuleBasedLabeler()
    review = make_review()
    labeler.label(review)
    assert labels.Purchase.FIRST_PURCHASE in review.labels

    for _ in range(5):
        stats.record_review(make_review(user="u", score=3))
    repeat = make_review(user="u", score=5)
    labeler.label(repeat)
    assert labels.Purchase.EXPERT_BUYER in repeat.labels


def test_repeat_label_for_middle_purchase_count():
    for _ in range(2):
        stats.record_review(make_review(user="u", score=3))
    review = make_review(user="u")
    RuleBasedLabeler().label(review)
    assert labels.Purchase.REPEAT_PURCHASE in review.labels


@pytest.mark.parametrize(
    ("source", "score", "expected"),
    [
        ("our_system", 5, labels.Satisfaction.SATISFIED),
        ("our_system", 1, labels.Satisfaction.DISSATISFIED),
        ("other_source", 4, labels.Satisfaction.SATISFIED),
        ("not_purchased", 5, labels.Satisfaction.INTERESTED),
    ],
)
def test_satisfaction_labels(source, score, expected):
    review = make_review(source, score)
    RuleBasedLabeler().label(review)
    assert expected in review.labels


def test_low_interest_has_no_satisfaction_label():
    review = make_review("not_purchased", 2)
    RuleBasedLabeler().label(review)
    assert not review.labels


def test_stats_records_categories_and_queues():
    local = _Stats()
    human = make_review()
    human.status = ReviewStatus("needs_human_review")
    rejected = make_review(user="u2")
    rejected.status = ReviewStatus.REJECTED
    approved = make_review(user="u3")
    approved.status = ReviewStatus.AUTO_APPROVED
    for item in (human, rejected, approved):
        local.record_review(item)
    data = local.get_user_stats("u3")
    assert data["total"] == 1
    assert data["purchase_count"] == 1
    assert data["purchase_count_by_category"]["home_appliances"] == 1
    assert local.human_review_queue == [human]


def test_stats_not_purchased_and_unknown_user():
    local = _Stats()
    review = make_review("not_purchased")
    review.status = ReviewStatus.AUTO_APPROVED
    local.record_review(review)
    assert local.get_user_stats("u")["purchase_count"] == 0
    unknown = local.get_user_stats("missing")
    unknown["total"] = 99
    assert local.get_user_stats("missing")["total"] == 0


def test_stats_reset():
    local = _Stats()
    review = make_review()
    review.status = ReviewStatus("auto_approved")
    local.record_review(review)
    local.reset()
    assert local.get_user_stats("u")["total"] == 0
    assert local.human_review_queue == []


def test_llm_labeler_is_explicitly_unimplemented():
    with pytest.raises(NotImplementedError):
        LLMLabeler().label(make_review())


def test_enum_values():
    assert PurchaseSource.OUR_SYSTEM.value == "our_system"
    assert labels.Purchase.FIRST_PURCHASE.value == "first_purchase"

