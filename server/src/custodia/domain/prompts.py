from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    key: str
    version: str
    system_prompt: str
    user_template: str
