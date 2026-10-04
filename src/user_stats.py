from __future__ import annotations

from copy import deepcopy
from collections import defaultdict

from src.domain import PurchaseSource, ReviewStatus
from src.models.base import Review


class _Stats:
    """In-memory statistics and processing history for reviews."""

    @staticmethod
    def _create_new_user_counters() -> defaultdict[str, int | defaultdict]:
        """Create the counter structure used for a new user."""
        new_dict: defaultdict[str, int | defaultdict]
        new_dict = defaultdict(int)
        new_dict["purchase_count_by_category"] = defaultdict(int)
        return new_dict

    def __init__(self) -> None:
        self._user_stats: dict[str, defaultdict] = {}
        self.human_review_queue: list[Review] = []
        self.history: set[str] = set()

    def record_review(self, review: Review) -> None:
        """Update user statistics, history, and the human-review queue."""
        if review.user_id not in self._user_stats:
            self._user_stats[review.user_id] = self._create_new_user_counters()

        user = self._user_stats[review.user_id]

        # total and per-status counters
        status = review.status
        user["total"] += 1
        user[f"status_{getattr(status, 'value', status)}"] += 1

        # purchase counters (overall and per category)
        is_purchased = review.purchase_source != PurchaseSource.NOT_PURCHASED
        user["purchase_count"] += int(is_purchased)
        if is_purchased:
            user["purchase_count_by_category"][review.product_category] += 1

        # history and human-review queue
        self.history.add(review.review_id)
        if status == ReviewStatus.NEEDS_HUMAN_REVIEW:
            self.human_review_queue.append(review)

    def get_user_stats(self, user_id: str) -> dict:
        """Return a defensive copy of one user's statistics."""
        counters = self._user_stats.get(user_id)
        if counters is None:
            counters = self._create_new_user_counters()
        return deepcopy(counters)

    def __contains__(self, review: Review):
        """Return whether the review ID has already been processed."""
        return review.review_id in self.history

    def reset(self) -> None:
        """Clear statistics, queues, and processing history."""
        self._user_stats.clear()
        self.human_review_queue.clear()
        self.history.clear()


stats = _Stats()