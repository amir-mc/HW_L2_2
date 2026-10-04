from src.exceptions import (
    ConfigLoadError,
    HumanReviewRequiredError,
    InvalidFieldValueError,
    MissingRequiredFieldError,
    RejectedContentError,
    ReviewError,
    ReviewValidationError,
    UnauthorizedFieldError,
    InvalidProductCategoryError,
    RepeatedReviewError,
    PipelineError,
)


def test_exception_messages():
    assert str(ConfigLoadError("x.json", "bad")) == "Failed to load configuration 'x.json': bad"
    assert str(MissingRequiredFieldError("name")) == "Required field 'name' has no value."
    assert "Invalid value" in str(InvalidFieldValueError("x", 1))
    assert "not authorized" in str(UnauthorizedFieldError("x", "other_source"))
    assert "rejected word" in str(RejectedContentError("bad"))
    assert "Human review is required" in str(HumanReviewRequiredError("flag"))

def test_exceptions_hierarchy():
    assert issubclass(ConfigLoadError, ReviewError)
    assert issubclass(RepeatedReviewError, PipelineError)
    assert issubclass(ReviewValidationError, ReviewError)
    assert issubclass(InvalidProductCategoryError, ReviewError)
    assert issubclass(MissingRequiredFieldError, ReviewValidationError)
    assert issubclass(InvalidFieldValueError, ReviewValidationError)
    assert issubclass(UnauthorizedFieldError, ReviewValidationError)
    assert issubclass(RejectedContentError, ReviewValidationError)
    assert issubclass(HumanReviewRequiredError, ReviewValidationError)