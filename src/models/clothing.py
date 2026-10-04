from src.models.base import Review


class ClothingReview(Review):
    """Review model for clothing products."""

    _product_category = "clothing"

    # These tuples extend the rules inherited from the base review.
    REQUIRED_FIELDS = Review.REQUIRED_FIELDS + ("size", "color")
    BUYER_ONLY_FIELDS = Review.BUYER_ONLY_FIELDS + ("fit_rating",)
