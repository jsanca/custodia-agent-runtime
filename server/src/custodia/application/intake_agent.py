from custodia.application.ports import (
    AppliesAgentGuardrails,
    GeneratesText,
    LoadsPatientAdministrativeProfile,
    RetrievesPolicyContext,
    RetrievesPromptTemplate,
    SavesAuditEvents,
)
from custodia.domain.agents import AgentAnswer, SuggestedAction
from custodia.domain.audit import AuditAction, AuditEvent
from custodia.domain.identity import Principal
from custodia.domain.prompts import PromptTemplate

_INTAKE_PROMPT_KEY = "intake.answer_question"


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
        prompt_catalog: RetrievesPromptTemplate,
    ) -> None:
        self._patient_profile_loader = patient_profile_loader
        self._policy_context_retriever = policy_context_retriever
        self._text_generator = text_generator
        self._audit_recorder = audit_recorder
        self._agent_guardrail = agent_guardrail
        self._prompt_catalog = prompt_catalog

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

        missing_document_labels = patient_profile.missing_document_labels()
        pending_review_document_labels = patient_profile.pending_review_document_labels()
        requires_review = len(missing_document_labels) > 0
        suggested_actions = self._build_suggested_actions(missing_document_labels)

        retrieved_policy_chunks = self._policy_context_retriever.retrieve(question)

        prompt_template = self._prompt_catalog.get_prompt(_INTAKE_PROMPT_KEY)
        rendered_user_prompt = self._render_user_prompt(
            prompt_template,
            question,
            patient_profile.display_name,
            missing_document_labels,
            pending_review_document_labels,
            retrieved_policy_chunks,
        )
        raw_llm_answer = self._text_generator.generate(rendered_user_prompt)

        guarded_answer = AgentAnswer(
            answer=raw_llm_answer,
            suggested_actions=suggested_actions,
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

    def _build_suggested_actions(
        self,
        missing_document_labels: tuple[str, ...],
    ) -> tuple[SuggestedAction, ...]:
        if not missing_document_labels:
            return ()
        return (
            SuggestedAction(
                description=f"Collect missing documents: {', '.join(missing_document_labels)}",
                requires_human_review=False,
            ),
        )

    def _render_user_prompt(
        self,
        prompt_template: PromptTemplate,
        question: str,
        patient_display_name: str,
        missing_document_labels: tuple[str, ...],
        pending_review_document_labels: tuple[str, ...],
        retrieved_policy_chunks: list[str],
    ) -> str:
        if retrieved_policy_chunks:
            policy_context = "Relevant policy context:\n" + "\n".join(
                f"- {chunk}" for chunk in retrieved_policy_chunks
            )
        else:
            policy_context = "No relevant policy context found."

        return prompt_template.user_template.format(
            question=question,
            patient_display_name=patient_display_name,
            missing_document_labels=", ".join(missing_document_labels) or "none",
            pending_review_document_labels=", ".join(pending_review_document_labels) or "none",
            policy_context=policy_context,
        )
