from enum import Enum as _Enum


class Purchase(str, _Enum):
    """Labels describing a user's purchase history."""

    FIRST_PURCHASE = "first_purchase"
    REPEAT_PURCHASE = "repeat_purchase"
    EXPERT_BUYER = "expert_buyer"


class Satisfaction(str, _Enum):
    """Labels describing satisfaction or buying interest."""

    SATISFIED = "satisfied_buyer"
    DISSATISFIED = "dissatisfied_buyer"
    INTERESTED = "interested_in_buying"
