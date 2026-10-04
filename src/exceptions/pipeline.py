class PipelineError(Exception):
    """Base exception for pipeline-specific errors."""


class RepeatedReviewError(PipelineError):
    """Raised when a review is detected as already processed."""

    def __init__(self, review_id: str) -> None:
        self.review_id = review_id
        super().__init__(f"Review '{review_id}' has already been processed.")