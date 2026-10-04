import pytest

from src.exceptions import InvalidProductCategoryError
from src.models import ClothingReview, ElectronicsReview, HomeApplianceReview
from src.pipeline.factory import review_factory


@pytest.mark.parametrize(
    ("category", "cls", "extra"),
    [
        ("clothing", ClothingReview, {"size": "L", "color": "blue"}),
        ("electronics", ElectronicsReview, {"warranty_months": 24}),
        ("home_appliances", HomeApplianceReview, {}),
    ],
)
def test_review_factory(category, cls, extra):
    data = {
        "product_category": category,
        "review_id": "r",
        "user_id": "u",
        "product_id": "p",
        "purchase_source": "not_purchased",
        "overall_satisfaction": 3,
        "review_text": "متن",
        **extra,
    }
    review = review_factory(category, data)
    assert isinstance(review, cls)


def test_review_factory_does_not_mutate_input():
    data = {
        "product_category": "home_appliances",
        "review_id": "r",
        "user_id": "u",
        "product_id": "p",
        "purchase_source": "not_purchased",
        "overall_satisfaction": 3,
        "review_text": "متن",
    }
    original = data.copy()
    review_factory("home_appliances", data)
    assert data == original


def test_review_factory_unknown_category():
    with pytest.raises(InvalidProductCategoryError):
        review_factory("unknown", {})
