from __future__ import annotations

from typing import Any

from src.exceptions import MCPConnectionError


def create_production_client(connections: dict[str, dict[str, Any]]) -> Any:
    """Create the official LangChain MCP adapter when its extra is installed."""

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as exc:
        raise MCPConnectionError(
            "production MCP adapter requires the optional 'mcp' dependency group"
        ) from exc
    return MultiServerMCPClient(connections)
