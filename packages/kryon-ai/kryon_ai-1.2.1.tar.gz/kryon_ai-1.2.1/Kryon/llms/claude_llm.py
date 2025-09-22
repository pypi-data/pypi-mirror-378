import anthropic
from .base import BaseLLM

class ClaudeLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(model)
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
