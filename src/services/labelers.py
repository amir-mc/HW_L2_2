from typing import Protocol

from src.domain import PurchaseSource, labels
from src.models.base import Review
from src.user_stats import stats

EXPERT_PURCHASE_THRESHOLD = 5


class ReviewLabeler(Protocol):
    """Protocol implemented by objects that assign labels to reviews."""

    def label(self, review: Review) -> None:  # pragma: no cover
        """Add zero or more labels to a review."""
        ...  # pragma: no cover


class RuleBasedLabeler:
    """Assign labels using deterministic business rules."""

    def label(self, review: Review) -> None:
        self._review = review
        is_purchased = review.purchase_source != PurchaseSource.NOT_PURCHASED
        if is_purchased:
            self._add_purchase_label()
        self._add_satisfaction_label(
            is_purchased=is_purchased,
            satisfaction_score=review.overall_satisfaction,
        )

    def _add_purchase_label(self) -> None:
        """Add a label based on the user's purchase history."""
        previous = stats.get_user_stats(self._review.user_id)["purchase_count"]
        if previous == 0:
            label = labels.Purchase.FIRST_PURCHASE
        elif previous < EXPERT_PURCHASE_THRESHOLD:
            label = labels.Purchase.REPEAT_PURCHASE
        else:
            label = labels.Purchase.EXPERT_BUYER
        self._review.labels.add(label)

    def _add_satisfaction_label(
        self, *, is_purchased: bool, satisfaction_score: int
    ) -> None:
        """Add a satisfaction label when the score qualifies."""
        if is_purchased:
            if satisfaction_score >= 4:
                self._review.labels.add(labels.Satisfaction.SATISFIED)
            elif satisfaction_score <= 2:
                self._review.labels.add(labels.Satisfaction.DISSATISFIED)
        elif satisfaction_score >= 4:
            self._review.labels.add(labels.Satisfaction.INTERESTED)


class LLMLabeler:
    """Placeholder for a future LLM-based labeling strategy."""

    def label(self, review: Review) -> None:
        raise NotImplementedError("LLMLabeler is not implemented yet.")