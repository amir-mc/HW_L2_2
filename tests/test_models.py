import pytest

from src.domain import PurchaseSource, ReviewStatus
from src.exceptions import (
    InvalidFieldValueError,
    MissingRequiredFieldError,
    UnauthorizedFieldError,
)
from src.models.base import Review
from src.models import ClothingReview, ElectronicsReview, HomeApplianceReview


def valid_base(**extra):
    data = {
        "review_id": "r1",
        "user_id": "u1",
        "product_id": "p1",
        "purchase_source": "our_system",
        "overall_satisfaction": 5,
        "review_text": "عالی",
    }
    data.update(extra)
    return data


def test_base_review_defaults_and_repr():
    review = Review(**valid_base())
    assert review.product_category == "general"
    assert review.status == ReviewStatus.UNDEFINED
    assert review.labels == set()
    assert review.timestamp
    assert "_input_fields" in review.__dict__ or review._input_fields


@pytest.mark.parametrize("field", Review.REQUIRED_FIELDS)
def test_missing_required_field(field):
    data = valid_base()
    data[field] = None
    with pytest.raises(MissingRequiredFieldError):
        Review(**data).validate()


@pytest.mark.parametrize("value", [True, 0, 6, "5"])
def test_invalid_satisfaction(value):
    with pytest.raises(InvalidFieldValueError):
        Review(**valid_base(overall_satisfaction=value)).validate()


@pytest.mark.parametrize("field", ["review_id", "user_id", "product_id", "review_text"])
def test_invalid_string_field(field):
    with pytest.raises(InvalidFieldValueError):
        Review(**valid_base(**{field: 10})).validate()


def test_invalid_purchase_source():
    with pytest.raises(InvalidFieldValueError):
        Review(**valid_base(purchase_source="unknown")).validate()


def test_buyer_only_field_rejected_for_non_buyer():
    with pytest.raises(UnauthorizedFieldError):
        Review(**valid_base(
            purchase_source="not_purchased",
            would_recommend=True,
        )).validate()


@pytest.mark.parametrize("source", ["other_source", "not_purchased"])
def test_system_only_fields_rejected_for_other_sources(source):
    with pytest.raises(UnauthorizedFieldError):
        Review(**valid_base(
            purchase_source=source,
            discount_code_used=True,
        )).validate()


def test_our_system_fields_are_allowed():
    review = Review(**valid_base(
        discount_code_used=False,
        delivery_experience_rating=4,
    ))
    review.validate()
    assert review.purchase_source == PurchaseSource.OUR_SYSTEM


def test_clothing_fields_and_category():
    review = ClothingReview(**valid_base(size="M", color="black"))
    review.validate()
    assert review.product_category == "clothing"
    assert "size" in review._input_fields
    assert "fit_rating" in review._input_fields


def test_electronics_validation():
    review = ElectronicsReview(**valid_base(warranty_months=12))
    review.validate()
    assert review.product_category == "electronics"


@pytest.mark.parametrize("value", [-1, 1.5, True, "12"])
def test_invalid_electronics_warranty(value):
    review = ElectronicsReview(**valid_base(warranty_months=value))
    with pytest.raises(InvalidFieldValueError):
        review.validate()


def test_home_appliances_category():
    review = HomeApplianceReview(**valid_base())
    review.validate()
    assert review.product_category == "home_appliances"


def test_timestamp_is_preserved():
    review = Review(**valid_base(timestamp="fixed"))
    assert review.timestamp == "fixed"
