from groq import Groq
from .base import BaseLLM

class GroqLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        super().__init__(model)
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
