from .review_exceptions import ReviewError


class ReviewValidationError(ReviewError):
    """Base exception for review validation errors."""


class MissingRequiredFieldError(ReviewValidationError):
    """Raised when a required review field has no value."""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name
        super().__init__(f"Required field '{field_name}' has no value.")


class InvalidFieldValueError(ReviewValidationError):
    """Raised when a field contains an invalid value."""

    def __init__(self, field_name: str, value) -> None:
        self.field_name = field_name
        self.value = value
        super().__init__(f"Invalid value for field '{field_name}': {value!r}")


class UnauthorizedFieldError(ReviewValidationError):
    """Raised when a field is not allowed for the purchase source."""

    def __init__(self, field_name: str, purchase_source) -> None:
        self.field_name = field_name
        self.purchase_source = purchase_source
        source = getattr(purchase_source, "value", purchase_source)
        super().__init__(
            f"Field '{field_name}' is not authorized for purchase source '{source}'."
        )


class RejectedContentError(ReviewValidationError):
    """Raised when review text contains a rejected word."""

    def __init__(self, matched_word: str) -> None:
        self.matched_word = matched_word
        super().__init__(f"Review text contains a rejected word: '{matched_word}'")


class HumanReviewRequiredError(ReviewValidationError):
    """Raised when automated processing should be reviewed by a person."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Human review is required: {reason}")