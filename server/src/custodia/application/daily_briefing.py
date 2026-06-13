from dataclasses import dataclass
from datetime import date

from custodia.application.ports import GeneratesText, SavesAuditEvents
from custodia.domain.audit import AuditAction, AuditEvent
from custodia.domain.identity import Principal
from custodia.domain.tasks import AdminTask


@dataclass(frozen=True)
class DailyBriefing:
    briefing_date: date
    incomplete_intake_count: int
    overdue_task_count: int
    overdue_tasks: tuple[AdminTask, ...]
    summary: str
    is_ai_assisted: bool


class DailyBriefingService:
    def __init__(
        self,
        text_generator: GeneratesText,
        audit_recorder: SavesAuditEvents,
    ) -> None:
        self._text_generator = text_generator
        self._audit_recorder = audit_recorder

    def generate(
        self,
        principal: Principal,
        briefing_date: date,
        incomplete_intake_count: int,
        overdue_tasks: list[AdminTask],
    ) -> DailyBriefing:
        prompt = (
            f"Date: {briefing_date}\n"
            f"Incomplete intakes: {incomplete_intake_count}\n"
            f"Overdue tasks: {len(overdue_tasks)}\n"
            "Provide a brief, factual administrative summary for the operations team. "
            "Do not include clinical recommendations."
        )
        summary = self._text_generator.generate(prompt)

        self._audit_recorder.save(
            AuditEvent(
                action=AuditAction.DAILY_BRIEFING_GENERATED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                agent_name="DailyBriefingService",
            )
        )

        return DailyBriefing(
            briefing_date=briefing_date,
            incomplete_intake_count=incomplete_intake_count,
            overdue_task_count=len(overdue_tasks),
            overdue_tasks=tuple(overdue_tasks),
            summary=summary,
            is_ai_assisted=True,
        )
