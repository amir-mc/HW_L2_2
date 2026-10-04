from abc import ABC, abstractmethod

from src.models.base import Review
from src.config import ConfigManager
from src.exceptions import RejectedContentError, HumanReviewRequiredError


class ReviewValidator(ABC):
    """Abstract strategy for validating a review."""

    @abstractmethod
    def validate(self, review: Review) -> None:  # pragma: no cover
        """Validate a review or raise an appropriate domain exception."""
        ...  # pragma: no cover


class SelfBasedValidator(ReviewValidator):
    """Validator that delegates to the review model's own validation."""

    def validate(self, review: Review) -> None:
        review.validate()


class WordFilterValidator(SelfBasedValidator):
    """Validate a review and inspect its text against configured word lists."""

    def __init__(self) -> None:
        super().__init__()

    def validate(self, review: Review) -> None:
        super().validate(review)

        config = ConfigManager(review.product_category)
        text = review.review_text.casefold()

        for word in config.reject_words:
            if word and word.casefold() in text:
                raise RejectedContentError(word)

        for word in config.review_words:
            if word and word.casefold() in text:
                raise HumanReviewRequiredError(f"text contains flagged word '{word}'")