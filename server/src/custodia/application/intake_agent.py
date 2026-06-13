from custodia.application.ports import (
    AppliesAgentGuardrails,
    GeneratesText,
    LoadsPatientAdministrativeProfile,
    RetrievesPolicyContext,
    SavesAuditEvents,
)
from custodia.domain.agents import AgentAnswer, SuggestedAction
from custodia.domain.audit import AuditAction, AuditEvent
from custodia.domain.identity import Principal
from custodia.domain.intake import IntakeStatus


class PatientNotFoundError(Exception):
    pass


class IntakeAgentService:
    def __init__(
        self,
        profiles: LoadsPatientAdministrativeProfile,
        policies: RetrievesPolicyContext,
        llm: GeneratesText,
        audit: SavesAuditEvents,
        guardrails: AppliesAgentGuardrails,
    ) -> None:
        self._profiles = profiles
        self._policies = policies
        self._llm = llm
        self._audit = audit
        self._guardrails = guardrails

    def answer_question(
        self,
        principal: Principal,
        patient_id: str,
        question: str,
    ) -> AgentAnswer:
        profile = self._profiles.load(patient_id)
        if profile is None:
            raise PatientNotFoundError(patient_id)

        self._audit.save(
            AuditEvent(
                action=AuditAction.INTAKE_PROFILE_VIEWED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                resource_type="patient",
                resource_id=patient_id,
            )
        )

        missing = [d.name for d in profile.documents if d.status == IntakeStatus.MISSING]
        pending = [d.name for d in profile.documents if d.status == IntakeStatus.PENDING_REVIEW]

        policy_chunks = self._policies.retrieve(question)

        prompt = self._build_prompt(question, profile.display_name, missing, pending, policy_chunks)
        raw_answer = self._llm.generate(prompt)

        requires_review = len(missing) > 0
        actions: tuple[SuggestedAction, ...] = ()
        if missing:
            actions = (
                SuggestedAction(
                    description=f"Collect missing documents: {', '.join(missing)}",
                    requires_human_review=False,
                ),
            )

        answer = AgentAnswer(
            answer=raw_answer,
            suggested_actions=actions,
            requires_human_review=requires_review,
            source_references=tuple(policy_chunks),
            is_ai_assisted=True,
        )
        answer = self._guardrails.check(answer, {"patient_id": patient_id})

        self._audit.save(
            AuditEvent(
                action=AuditAction.INTAKE_AGENT_ANSWERED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                resource_type="patient",
                resource_id=patient_id,
                agent_name="IntakeAgentService",
                human_review_required=answer.requires_human_review,
            )
        )

        return answer

    def _build_prompt(
        self,
        question: str,
        display_name: str,
        missing: list[str],
        pending: list[str],
        policy_chunks: list[str],
    ) -> str:
        parts = [
            f"Question: {question}",
            f"Patient display name: {display_name}",
            f"Missing documents: {missing or 'none'}",
            f"Pending review: {pending or 'none'}",
        ]
        if policy_chunks:
            parts.append("Relevant policy context:")
            parts.extend(f"- {chunk}" for chunk in policy_chunks)
        parts.append(
            "Provide an administrative answer only. "
            "Do not give clinical advice or make clinical judgments."
        )
        return "\n".join(parts)
