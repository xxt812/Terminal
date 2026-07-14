import os
import sys
import json
from src.agent_core.protocol import AgentMessage

class MCPClient:
    def __init__(self):
        self.input = sys.stdin
        self.output = sys.stdout

    def generate(self, prompt: str) -> str:
        payload = {"prompt": prompt, "model": "claude-sonnet-4-6"}
        self.output.write(json.dumps(payload) + "\n")
        self.output.flush()

        response = self.input.readline().strip()
        return response
