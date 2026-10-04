from enum import Enum


class ReviewStatus(str, Enum):
    """Possible processing states for a review."""

    UNDEFINED = "undefined"
    REJECTED = "rejected"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    AUTO_APPROVED = "auto_approved"
    MANUAL_APPROVED = "manual_approved"


class PurchaseSource(str, Enum):
    """Possible sources or states of a product purchase."""

    OUR_SYSTEM = "our_system"
    OTHER_SOURCE = "other_source"
    NOT_PURCHASED = "not_purchased"
