class BaseLLM:
    """Base interface for all LLM providers."""

    def __init__(self, model: str):
        self.model = model

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Each LLM must implement generate()")
