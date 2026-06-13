from custodia.application.ports import GeneratesText, RetrievesPolicyContext, SavesAuditEvents
from custodia.domain.agents import AgentAnswer
from custodia.domain.audit import AuditAction, AuditEvent
from custodia.domain.identity import Principal


class PolicyAgentService:
    def __init__(
        self,
        policies: RetrievesPolicyContext,
        llm: GeneratesText,
        audit: SavesAuditEvents,
    ) -> None:
        self._policies = policies
        self._llm = llm
        self._audit = audit

    def answer_question(self, principal: Principal, question: str) -> AgentAnswer:
        chunks = self._policies.retrieve(question)

        self._audit.save(
            AuditEvent(
                action=AuditAction.POLICY_CONTEXT_RETRIEVED,
                actor_subject=principal.subject,
                actor_email=principal.email,
                actor_roles=frozenset(str(r) for r in principal.roles),
                outcome="success",
                agent_name="PolicyAgentService",
            )
        )

        if not chunks:
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
            + "\n".join(f"- {c}" for c in chunks)
            + "\nAnswer based only on the policy context above. Do not give clinical advice."
        )
        raw_answer = self._llm.generate(prompt)

        return AgentAnswer(
            answer=raw_answer,
            suggested_actions=(),
            requires_human_review=False,
            source_references=tuple(chunks),
            is_ai_assisted=True,
        )
