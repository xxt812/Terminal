from .chat_model import BaseLLM

class LLMProviderAdapter:
    def __init__(self):
        self.providers = {
            "mcp": BaseLLM(provider="mcp"),
            # Future: add other providers here
        }

    def get_model(self, provider: str) -> BaseLLM:
        return self.providers.get(provider, self.providers["mcp"])
