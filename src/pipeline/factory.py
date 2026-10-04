from typing import Any, Callable

from src.exceptions import InvalidProductCategoryError
from src.models import (
    ClothingReview,
    ElectronicsReview,
    HomeApplianceReview,
)
from src.models.base import Review

ReviewFactory = Callable[[str, dict[str, Any]], Review]

_REVIEW_TYPES = {
    "clothing": ClothingReview,
    "electronics": ElectronicsReview,
    "home_appliances": HomeApplianceReview,
}


def review_factory(product_category: str, data: dict[str, Any]) -> Review:
    """Create the appropriate review model for a product category."""
    key = product_category.strip().lower() if isinstance(product_category, str) else None
    review_class = _REVIEW_TYPES.get(key)
    if review_class is None:
        raise InvalidProductCategoryError(product_category)
    # Pass a shallow copy so the caller's dict is never touched.
    return review_class(**dict(data))