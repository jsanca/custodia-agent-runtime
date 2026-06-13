class FakeLlm:
    def __init__(self, response: str = "This is a fake LLM response.") -> None:
        self._response = response
        self.last_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self._response
