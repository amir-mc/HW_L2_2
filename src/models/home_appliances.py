from src.models.base import Review


class HomeApplianceReview(Review):
    """Review model for home-appliance products."""

    _product_category = "home_appliances"
