from __future__ import annotations

import asyncio

from src.mcp.client import MCPClient, MCPTool
from src.mcp.config_loader import MCPServerConfig


class MCPRegistry:
    """Own MCP client lifecycles and aggregate discovered tools."""

    def __init__(self, configs: dict[str, MCPServerConfig] | None = None) -> None:
        self._clients = {
            name: MCPClient.from_config(config) for name, config in (configs or {}).items()
        }

    def add(self, client: MCPClient) -> None:
        name = client.config.name
        if name in self._clients:
            raise ValueError(f"MCP server already registered: {name}")
        self._clients[name] = client

    async def connect_all(self) -> None:
        connected: list[MCPClient] = []
        try:
            for client in self._clients.values():
                await client.connect()
                connected.append(client)
        except Exception:
            await asyncio.gather(*(client.close() for client in connected))
            raise

    async def close_all(self) -> None:
        await asyncio.gather(*(client.close() for client in self._clients.values()))

    def tools(self) -> list[MCPTool]:
        return [tool for client in self._clients.values() for tool in client.tools]

    def clients(self) -> dict[str, MCPClient]:
        return dict(self._clients)
