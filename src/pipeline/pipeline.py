from functools import wraps
from time import perf_counter
from typing import Any, Callable

from src.domain import ReviewStatus
from src.exceptions import (
    HumanReviewRequiredError,
    ReviewValidationError,
    RepeatedReviewError,
)
from src.models.base import Review
from src.pipeline.factory import ReviewFactory
from src.services.labelers import ReviewLabeler
from src.services.validators import ReviewValidator
from src.user_stats import stats


def log_processing_time(func: Callable) -> Callable:
    """Print the execution time of a wrapped function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - start
        print(f"{func.__name__} completed in {elapsed:.4f} seconds")
        return result

    return wrapper


class ReviewPipeline:
    """Coordinate review creation, validation, labeling, and statistics."""

    def __init__(
        self,
        factory: ReviewFactory,
        validator: ReviewValidator,
        labeler: ReviewLabeler,
        repeated_review_error=False,
    ) -> None:
        self._factory = factory
        self._validator = validator
        self._labeler = labeler
        self._repeated_review_error = repeated_review_error

    def process(self, raw_data: dict[str, Any]) -> Review:
        """Process one raw review and return its final model."""
        review = self._factory(raw_data.get("product_category"), raw_data)

        if self._repeated_review_error and review in stats:
            raise RepeatedReviewError(review.review_id)

        try:
            self._validator.validate(review)
        except HumanReviewRequiredError:
            review.status = ReviewStatus.NEEDS_HUMAN_REVIEW
        except ReviewValidationError:
            review.status = ReviewStatus.REJECTED

        if review.status == ReviewStatus.UNDEFINED:
            try:
                self._labeler.label(review)
            except HumanReviewRequiredError:
                review.status = ReviewStatus.NEEDS_HUMAN_REVIEW

        if review.status == ReviewStatus.UNDEFINED:
            review.status = ReviewStatus.AUTO_APPROVED

        stats.record_review(review)
        return review

    @log_processing_time
    def batch_process(
        self, input_data: list[dict[str, Any]]
    ) -> dict[ReviewStatus, list[Review]]:
        """Process a batch and group successful results by status."""
        grouped: dict[ReviewStatus, list[Review]] = {}
        for raw_data in input_data:
            try:
                review = self.process(raw_data)
            except RepeatedReviewError:
                continue
            grouped.setdefault(review.status, []).append(review)
        return grouped