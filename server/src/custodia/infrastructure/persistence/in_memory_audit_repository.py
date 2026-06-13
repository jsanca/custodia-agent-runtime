from custodia.domain.audit import AuditEvent


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def save(self, event: AuditEvent) -> None:
        self.events.append(event)
