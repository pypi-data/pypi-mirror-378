import google.generativeai as genai
from .base import BaseLLM

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        super().__init__(model)
        genai.configure(api_key=api_key)
        self.model_obj = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        resp = self.model_obj.generate_content(prompt)
        return resp.text.strip()
