from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class AuditAction(StrEnum):
    INTAKE_PROFILE_VIEWED = "INTAKE_PROFILE_VIEWED"
    INTAKE_AGENT_ANSWERED = "INTAKE_AGENT_ANSWERED"
    POLICY_CONTEXT_RETRIEVED = "POLICY_CONTEXT_RETRIEVED"
    DAILY_BRIEFING_GENERATED = "DAILY_BRIEFING_GENERATED"
    MCP_TOOL_INVOKED = "MCP_TOOL_INVOKED"
    ADMIN_TASK_CREATED = "ADMIN_TASK_CREATED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    TOOL_CALL_DENIED = "TOOL_CALL_DENIED"
    TOOL_CALL_COMPLETED = "TOOL_CALL_COMPLETED"


@dataclass(frozen=True)
class AuditEvent:
    action: AuditAction
    actor_subject: str
    actor_email: str
    actor_roles: frozenset[str]
    outcome: str
    resource_type: str | None = None
    resource_id: str | None = None
    agent_name: str | None = None
    tool_name: str | None = None
    human_review_required: bool = False
    trace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
