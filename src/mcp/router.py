from __future__ import annotations

from typing import Any

from src.exceptions import MCPToolError
from src.mcp.client import MCPTool


class MCPToolRouter:
    """Route tool calls to the server that advertised each tool."""

    def __init__(self, tools: list[MCPTool] | None = None) -> None:
        self._tools: dict[str, MCPTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: MCPTool, *, qualified: bool = False) -> str:
        name = f"{tool.server_name}.{tool.name}" if qualified else tool.name
        if name in self._tools:
            raise ValueError(f"duplicate MCP tool route: {name}")
        self._tools[name] = tool
        return name

    def unregister_server(self, server_name: str) -> None:
        self._tools = {
            name: tool for name, tool in self._tools.items() if tool.server_name != server_name
        }

    async def call(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise MCPToolError(f"unknown MCP tool: {name}")
        return await tool.invoke(arguments or {})

    def descriptions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters,
                "server": tool.server_name,
            }
            for name, tool in sorted(self._tools.items())
        ]
