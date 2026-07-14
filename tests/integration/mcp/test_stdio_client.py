import asyncio
import sys
from pathlib import Path

import pytest

from src.mcp.client import MCPClient

pytestmark = pytest.mark.integration


def test_stdio_server_discovery_and_call() -> None:
    server = Path(__file__).parents[2] / "fixtures" / "mcp_stdio_server.py"
    client = MCPClient(
        name="fixture",
        command=sys.executable,
        args=[str(server)],
        timeout=5,
    )

    async def exercise() -> tuple[list[object], str]:
        async with client:
            tools = await client.list_tools()
            result = await client.call_tool("echo", {"text": "hello"})
        return tools, result

    tools, result = asyncio.run(exercise())

    assert tools[0].name == "echo"
    assert result == "echo: hello"
