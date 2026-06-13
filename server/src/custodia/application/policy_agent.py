from custodia.application.ports import GeneratesText, RetrievesPolicyContext, SavesAuditEvents
from custodia.domain.agents import AgentAnswer
from custodia.domain.audit import AuditAction, AuditEvent
from custodia.domain.identity import Principal


class PolicyAgentService:
    def __init__(
        self,
        policy_context_retriever: RetrievesPolicyContext,
        text_generator: GeneratesText,
        audit_recorder: SavesAuditEvents,
    ) -> None:
        self._policy_context_retriever = policy_context_retriever
        self._text_generator = text_generator
        self._audit_recorder = audit_recorder

    def answer_question(self, principal: Principal, question: str) -> AgentAnswer:
        retrieved_policy_chunks = self._policy_context_retriever.retrieve(question)

        self._audit_recorder.save(
            AuditEvent(
                action=AuditAction.POLICY_CONTEXT_RETRIEVED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                agent_name="PolicyAgentService",
            )
        )

        if not retrieved_policy_chunks:
            return AgentAnswer(
                answer="No relevant policy context found for that question.",
                suggested_actions=(),
                requires_human_review=False,
                source_references=(),
                is_ai_assisted=False,
            )

        prompt = (
            f"Question: {question}\n"
            "Relevant policy context:\n"
            + "\n".join(f"- {chunk}" for chunk in retrieved_policy_chunks)
            + "\nAnswer based only on the policy context above. Do not give clinical advice."
        )
        raw_llm_answer = self._text_generator.generate(prompt)

        return AgentAnswer(
            answer=raw_llm_answer,
            suggested_actions=(),
            requires_human_review=False,
            source_references=tuple(retrieved_policy_chunks),
            is_ai_assisted=True,
        )
