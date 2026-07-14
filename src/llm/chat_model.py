from src.agent_core.protocol import BaseChatModel

class BaseLLM(BaseChatModel):
    def __init__(self, provider: str = "mcp"):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        if self.provider == "mcp":
            return self._mcp_generate(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _mcp_generate(self, prompt: str) -> str:
        from .mcp_client import MCPClient
        return MCPClient().generate(prompt)
