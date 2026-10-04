class ReviewError(Exception):
    """Base exception for project-specific errors."""


class ConfigLoadError(ReviewError):
    """Raised when a configuration file cannot be loaded."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load configuration '{file_path}': {reason}")


class InvalidProductCategoryError(ReviewError):
    """Raised when a review category is not supported."""

    def __init__(self, product_category: str) -> None:
        self.product_category = product_category
        super().__init__(f"Unsupported product category: '{product_category}'")