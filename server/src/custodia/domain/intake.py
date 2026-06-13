from enum import StrEnum


class IntakeStatus(StrEnum):
    MISSING = "missing"
    COMPLETE = "complete"
    PENDING_REVIEW = "pending_review"
