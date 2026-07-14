import asyncio
from pathlib import Path
from typing import Any

import pytest

from src.exceptions import MCPToolError
from src.mcp.client import MCPTool
from src.mcp.config_loader import load_server_configs
from src.mcp.router import MCPToolRouter

pytestmark = pytest.mark.unit


def test_load_stdio_config(tmp_path: Path) -> None:
    source = tmp_path / "mcp.yaml"
    source.write_text(
        "mcpServers:\n  math:\n    transport: stdio\n    command: python\n    args: [server.py]\n",
        encoding="utf-8",
    )

    configs = load_server_configs(source)

    assert configs["math"].command == "python"
    assert configs["math"].args == ["server.py"]


def test_router_calls_registered_tool() -> None:
    async def caller(arguments: dict[str, Any]) -> str:
        return f"echo: {arguments['text']}"

    tool = MCPTool("echo", "Echo text", {"type": "object"}, "test", caller)
    router = MCPToolRouter([tool])

    assert asyncio.run(router.call("echo", {"text": "hello"})) == "echo: hello"


def test_router_rejects_unknown_tool() -> None:
    with pytest.raises(MCPToolError, match="unknown MCP tool"):
        asyncio.run(MCPToolRouter().call("missing"))
