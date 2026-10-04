from functools import cache
from datetime import datetime, timezone

from src.domain import PurchaseSource, ReviewStatus
from src.exceptions import (
    InvalidFieldValueError,
    MissingRequiredFieldError,
    UnauthorizedFieldError,
)


class Review:
    """Base domain model for a customer review."""

    _product_category = "general"

    REQUIRED_FIELDS = (
        "review_id",
        "user_id",
        "product_id",
        "purchase_source",
        "overall_satisfaction",
        "review_text",
    )
    BUYER_ONLY_FIELDS = (
        "would_recommend",
    )
    OUR_SYSTEM_ONLY_FIELDS = (
        "discount_code_used",
        "delivery_experience_rating",
    )

    def __init__(self, **kwargs) -> None:
        for field in self._input_fields:
            setattr(self, field, kwargs.get(field))
        self.timestamp = kwargs.get("timestamp") or self._generate_timestamp()
        self.labels = set()
        self.status = ReviewStatus.UNDEFINED

    @property
    @cache
    def _input_fields(self) -> tuple[str, ...]:
        """Return all fields accepted by the current review type."""
        return (
            self.REQUIRED_FIELDS
            + self.BUYER_ONLY_FIELDS
            + self.OUR_SYSTEM_ONLY_FIELDS
        )

    @property
    def product_category(self) -> str:
        """Return the category associated with this review model."""
        return self._product_category

    def validate(self) -> None:
        """Validate required fields, field types, and source-specific rules."""
        
        for field in self.REQUIRED_FIELDS:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise MissingRequiredFieldError(field)

        for field in ("review_id", "user_id", "product_id", "review_text"):
            value = getattr(self, field)
            if not isinstance(value, str):
                raise InvalidFieldValueError(field, value)

     
        score = self.overall_satisfaction
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise InvalidFieldValueError("overall_satisfaction", score)


        try:
            source = PurchaseSource(self.purchase_source)
        except (ValueError, TypeError):
            raise InvalidFieldValueError(
                "purchase_source", self.purchase_source
            ) from None
        self.purchase_source = source


        if source == PurchaseSource.NOT_PURCHASED:
            for field in self.BUYER_ONLY_FIELDS:
                if getattr(self, field, None) is not None:
                    raise UnauthorizedFieldError(field, source)
        if source != PurchaseSource.OUR_SYSTEM:
            for field in self.OUR_SYSTEM_ONLY_FIELDS:
                if getattr(self, field, None) is not None:
                    raise UnauthorizedFieldError(field, source)

    @staticmethod
    def _generate_timestamp() -> str:
        """Generate an ISO-8601 timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat()

    def __repr__(self) -> str:
        """Return a compact representation useful for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"review_id={getattr(self, 'review_id', None)!r}, "
            f"status={self.status!r})"
        )