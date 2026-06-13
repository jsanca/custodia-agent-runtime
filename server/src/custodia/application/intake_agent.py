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
        patient_profile_loader: LoadsPatientAdministrativeProfile,
        policy_context_retriever: RetrievesPolicyContext,
        text_generator: GeneratesText,
        audit_recorder: SavesAuditEvents,
        agent_guardrail: AppliesAgentGuardrails,
    ) -> None:
        self._patient_profile_loader = patient_profile_loader
        self._policy_context_retriever = policy_context_retriever
        self._text_generator = text_generator
        self._audit_recorder = audit_recorder
        self._agent_guardrail = agent_guardrail

    def answer_question(
        self,
        principal: Principal,
        patient_id: str,
        question: str,
    ) -> AgentAnswer:
        patient_profile = self._patient_profile_loader.load(patient_id)
        if patient_profile is None:
            raise PatientNotFoundError(patient_id)

        self._audit_recorder.save(
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

        missing_document_names = [
            document.name
            for document in patient_profile.documents
            if document.status == IntakeStatus.MISSING
        ]
        pending_review_document_names = [
            document.name
            for document in patient_profile.documents
            if document.status == IntakeStatus.PENDING_REVIEW
        ]

        retrieved_policy_chunks = self._policy_context_retriever.retrieve(question)

        prompt = self._build_prompt(
            question,
            patient_profile.display_name,
            missing_document_names,
            pending_review_document_names,
            retrieved_policy_chunks,
        )
        raw_llm_answer = self._text_generator.generate(prompt)

        requires_review = len(missing_document_names) > 0
        actions: tuple[SuggestedAction, ...] = ()
        if missing_document_names:
            actions = (
                SuggestedAction(
                    description=f"Collect missing documents: {', '.join(missing_document_names)}",
                    requires_human_review=False,
                ),
            )

        guarded_answer = AgentAnswer(
            answer=raw_llm_answer,
            suggested_actions=actions,
            requires_human_review=requires_review,
            source_references=tuple(retrieved_policy_chunks),
            is_ai_assisted=True,
        )
        guarded_answer = self._agent_guardrail.check(guarded_answer, {"patient_id": patient_id})

        self._audit_recorder.save(
            AuditEvent(
                action=AuditAction.INTAKE_AGENT_ANSWERED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                resource_type="patient",
                resource_id=patient_id,
                agent_name="IntakeAgentService",
                human_review_required=guarded_answer.requires_human_review,
            )
        )

        return guarded_answer

    def _build_prompt(
        self,
        question: str,
        display_name: str,
        missing_document_names: list[str],
        pending_review_document_names: list[str],
        retrieved_policy_chunks: list[str],
    ) -> str:
        parts = [
            f"Question: {question}",
            f"Patient display name: {display_name}",
            f"Missing documents: {missing_document_names or 'none'}",
            f"Pending review: {pending_review_document_names or 'none'}",
        ]
        if retrieved_policy_chunks:
            parts.append("Relevant policy context:")
            parts.extend(f"- {chunk}" for chunk in retrieved_policy_chunks)
        parts.append(
            "Provide an administrative answer only. "
            "Do not give clinical advice or make clinical judgments."
        )
        return "\n".join(parts)
