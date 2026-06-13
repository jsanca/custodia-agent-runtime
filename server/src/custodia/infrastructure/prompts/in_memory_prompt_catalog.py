from custodia.domain.prompts import PromptTemplate

_INTAKE_ANSWER_QUESTION = PromptTemplate(
    key="intake.answer_question",
    version="1.0",
    system_prompt=(
        "You are an administrative assistant for a mental health operations team. "
        "Answer only administrative questions about patient intake status and clinic policies. "
        "Never give clinical advice, make diagnoses, or recommend treatments. "
        "When clinical matters arise, flag the item for human review."
    ),
    user_template=(
        "Question: {question}\n"
        "Patient: {patient_display_name}\n"
        "Missing documents: {missing_document_labels}\n"
        "Pending review: {pending_review_document_labels}\n"
        "{policy_context}\n"
        "Provide an administrative answer only. "
        "Do not give clinical advice or make clinical judgments."
    ),
)

_PROMPTS: dict[str, PromptTemplate] = {
    _INTAKE_ANSWER_QUESTION.key: _INTAKE_ANSWER_QUESTION,
}


class InMemoryPromptCatalog:
    def get_prompt(self, prompt_key: str) -> PromptTemplate:
        if prompt_key not in _PROMPTS:
            raise KeyError(f"Prompt not found: {prompt_key!r}")
        return _PROMPTS[prompt_key]
