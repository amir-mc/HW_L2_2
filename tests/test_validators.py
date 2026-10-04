import pytest

from src.config import ConfigManager
from src.exceptions import HumanReviewRequiredError, RejectedContentError
from src.models import HomeApplianceReview
from src.services.validators import SelfBasedValidator, WordFilterValidator


def review(text):
    return HomeApplianceReview(
        review_id="r",
        user_id="u",
        product_id="p",
        purchase_source="not_purchased",
        overall_satisfaction=3,
        review_text=text,
    )


def test_self_based_validator():
    SelfBasedValidator().validate(review("خوب است"))


def test_word_filter_reject():
    with pytest.raises(RejectedContentError):
        WordFilterValidator().validate(review("این فرد کلاهبردار است"))


def test_word_filter_human_review():
    with pytest.raises(HumanReviewRequiredError):
        WordFilterValidator().validate(review("شکایت دارم"))


def test_word_filter_clean():
    WordFilterValidator().validate(review("خوب است"))


def test_config_manager_error_propagates(monkeypatch):
    def boom(_self):
        raise RuntimeError("boom")
    monkeypatch.setattr(ConfigManager, "reject_words", property(boom))
    with pytest.raises(RuntimeError):
        WordFilterValidator().validate(review("clean"))


def test_abstract_validator_implementation():
    class ConcreteValidator(SelfBasedValidator):
        pass
    ConcreteValidator().validate(review("ok"))
