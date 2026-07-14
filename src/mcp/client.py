from .mcp_client import MCPClient

class MCPClient:
    def __init__(self):
        self.client = MCPClient()

    def generate(self, prompt: str) -> str:
        return self.client.generate(prompt)
