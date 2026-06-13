from typing import Any

from custodia.domain.agents import AgentAnswer, SuggestedAction

_CLINICAL_KEYWORDS = frozenset(
    [
        "diagnos",
        "therapy",
        "treatment",
        "prescri",
        "self-harm",
        "suicid",
        "medication",
        "clinical",
    ]
)


class DefaultAgentGuardrails:
    def check(self, answer: AgentAnswer, context: dict[str, Any]) -> AgentAnswer:
        lower = answer.answer.lower()
        if any(kw in lower for kw in _CLINICAL_KEYWORDS):
            refusal = (
                "I can only assist with administrative matters. "
                "Please consult a qualified clinician for clinical questions."
            )
            return AgentAnswer(
                answer=refusal,
                suggested_actions=(
                    SuggestedAction(
                        description="Refer to a qualified clinician.",
                        requires_human_review=True,
                    ),
                ),
                requires_human_review=True,
                source_references=(),
                is_ai_assisted=True,
            )
        return answer
