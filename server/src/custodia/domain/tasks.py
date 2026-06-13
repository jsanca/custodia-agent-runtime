from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    OVERDUE = "overdue"


@dataclass(frozen=True)
class AdminTask:
    task_id: str
    title: str
    status: TaskStatus
    assigned_to: str | None
    due_at: datetime | None
    patient_id: str | None
