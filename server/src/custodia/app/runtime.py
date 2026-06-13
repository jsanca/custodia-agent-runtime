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

    profiles = InMemoryPatientRepository()
    policies = KeywordPolicyRetriever()
    llm = FakeLlm()
    audit = InMemoryAuditRepository()
    guardrails = DefaultAgentGuardrails()
    auth = FakePrincipal()

    intake_agent = IntakeAgentService(
        profiles=profiles,
        policies=policies,
        llm=llm,
        audit=audit,
        guardrails=guardrails,
    )
    policy_agent = PolicyAgentService(
        policies=policies,
        llm=llm,
        audit=audit,
    )
    daily_briefing = DailyBriefingService(
        llm=llm,
        audit=audit,
    )

    return Runtime(
        settings=settings,
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        daily_briefing=daily_briefing,
        auth=auth,
    )
