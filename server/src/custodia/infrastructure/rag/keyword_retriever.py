_POLICY_DOCUMENTS: list[str] = [
    "Patients must complete consent forms before scheduling a first appointment.",
    "Insurance verification must be completed within 5 business days of intake.",
    "No-show policy: patients who miss two consecutive appointments require staff follow-up.",
    "Patients with pending insurance verification may be provisionally scheduled "
    "pending admin review.",
    "All intake documents must be reviewed by a staff member before the first session.",
]


class KeywordPolicyRetriever:
    def retrieve(self, query: str) -> list[str]:
        lower = query.lower()
        return [
            doc
            for doc in _POLICY_DOCUMENTS
            if any(word in doc.lower() for word in lower.split())
        ]
