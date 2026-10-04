from src.exceptions import InvalidFieldValueError
from src.models.base import Review


class ElectronicsReview(Review):
    """Review model for electronics products."""

    _product_category = "electronics"

    REQUIRED_FIELDS = Review.REQUIRED_FIELDS + ("warranty_months",)
    BUYER_ONLY_FIELDS = Review.BUYER_ONLY_FIELDS + ("technical_issue_reported",)

    warranty_months: int
    technical_issue_reported: bool

    def validate(self) -> None:
        """Validate base review rules and electronics-specific fields."""
        super().validate()
        warranty = self.warranty_months
        if isinstance(warranty, bool) or not isinstance(warranty, int) or warranty < 0:
            raise InvalidFieldValueError("warranty_months", warranty)