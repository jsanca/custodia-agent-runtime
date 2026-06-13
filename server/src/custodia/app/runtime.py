from dataclasses import dataclass

from custodia.app.settings import CustodiaSettings
from custodia.application.daily_briefing import DailyBriefingService
from custodia.application.guardrails import DefaultAgentGuardrails
from custodia.application.intake_agent import IntakeAgentService
from custodia.application.policy_agent import PolicyAgentService
from custodia.infrastructure.identity.fake_auth import FakePrincipal
from custodia.infrastructure.llm.fake_llm import FakeLlm
from custodia.infrastructure.persistence.in_memory_audit_repository import InMemoryAuditRepository
from custodia.infrastructure.persistence.in_memory_patient_repository import (
    InMemoryPatientRepository,
)
from custodia.infrastructure.rag.keyword_retriever import KeywordPolicyRetriever


@dataclass(frozen=True)
class Runtime:
    settings: CustodiaSettings
    intake_agent: IntakeAgentService
    policy_agent: PolicyAgentService
    daily_briefing: DailyBriefingService
    auth: FakePrincipal


def build_runtime() -> Runtime:
    settings = CustodiaSettings()

    patient_profile_loader = InMemoryPatientRepository()
    policy_context_retriever = KeywordPolicyRetriever()
    text_generator = FakeLlm()
    audit_recorder = InMemoryAuditRepository()
    agent_guardrail = DefaultAgentGuardrails()
    auth = FakePrincipal()

    intake_agent = IntakeAgentService(
        patient_profile_loader=patient_profile_loader,
        policy_context_retriever=policy_context_retriever,
        text_generator=text_generator,
        audit_recorder=audit_recorder,
        agent_guardrail=agent_guardrail,
    )
    policy_agent = PolicyAgentService(
        policy_context_retriever=policy_context_retriever,
        text_generator=text_generator,
        audit_recorder=audit_recorder,
    )
    daily_briefing = DailyBriefingService(
        text_generator=text_generator,
        audit_recorder=audit_recorder,
    )

    return Runtime(
        settings=settings,
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        daily_briefing=daily_briefing,
        auth=auth,
    )
