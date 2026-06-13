from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class AgentRunStatus(StrEnum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


@dataclass(frozen=True)
class SuggestedAction:
    description: str
    requires_human_review: bool = False


@dataclass(frozen=True)
class AgentAnswer:
    answer: str
    suggested_actions: tuple[SuggestedAction, ...]
    requires_human_review: bool
    source_references: tuple[str, ...]
    is_ai_assisted: bool = True


@dataclass(frozen=True)
class AgentRun:
    run_id: str
    agent_name: str
    status: AgentRunStatus
    principal_subject: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
