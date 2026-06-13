from typing import Any, Protocol

from custodia.domain.agents import AgentAnswer
from custodia.domain.audit import AuditEvent
from custodia.domain.patients import PatientAdministrativeProfile
from custodia.domain.prompts import PromptTemplate


class LoadsPatientAdministrativeProfile(Protocol):
    def load(self, patient_id: str) -> PatientAdministrativeProfile | None:
        ...


class GeneratesText(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class SavesAuditEvents(Protocol):
    def save(self, event: AuditEvent) -> None:
        ...


class RetrievesPolicyContext(Protocol):
    def retrieve(self, query: str) -> list[str]:
        ...


class AppliesAgentGuardrails(Protocol):
    def check(self, answer: AgentAnswer, context: dict[str, Any]) -> AgentAnswer:
        ...


class RetrievesPromptTemplate(Protocol):
    def get_prompt(self, prompt_key: str) -> PromptTemplate:
        ...
