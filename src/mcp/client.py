from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

import httpx

from src.exceptions import MCPConnectionError, MCPProtocolError, MCPToolError
from src.mcp.config_loader import MCPServerConfig

ToolCaller = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class MCPTool:
    """A tool dynamically discovered from an MCP server."""

    name: str
    description: str
    parameters: dict[str, Any]
    server_name: str
    _caller: ToolCaller = field(repr=False, compare=False)

    async def invoke(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> str:
        payload = dict(arguments or {})
        payload.update(kwargs)
        return await self._caller(payload)


class MCPClient:
    """Minimal MCP bridge supporting line-delimited stdio and HTTP endpoints."""

    def __init__(
        self,
        name: str = "default",
        transport: str = "stdio",
        command: str | None = None,
        args: list[str] | None = None,
        url: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.config = MCPServerConfig(
            name=name,
            transport=transport,
            command=command,
            args=args or [],
            url=url,
            env=env or {},
            timeout=timeout,
        )
        self.tools: list[MCPTool] = []
        self._process: asyncio.subprocess.Process | None = None
        self._http: httpx.AsyncClient | None = None
        self._request_id = 0
        self._io_lock = asyncio.Lock()

    @classmethod
    def from_config(cls, config: MCPServerConfig) -> MCPClient:
        return cls(**config.model_dump())

    async def __aenter__(self) -> MCPClient:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.close()

    async def connect(self) -> None:
        if self._process is not None or self._http is not None:
            return
        try:
            if self.config.transport == "stdio":
                await self._connect_stdio()
            else:
                self._http = httpx.AsyncClient(
                    base_url=self.config.url or "", timeout=self.config.timeout
                )
            await self.refresh_tools()
        except Exception as exc:
            await self.close()
            if isinstance(exc, (MCPConnectionError, MCPProtocolError)):
                raise
            raise MCPConnectionError(f"failed to connect MCP server {self.config.name!r}") from exc

    async def refresh_tools(self) -> list[MCPTool]:
        result = await self._request("tools/list")
        raw_tools = result.get("tools", []) if isinstance(result, dict) else []
        if not isinstance(raw_tools, list):
            raise MCPProtocolError("tools/list result must contain a tools list")
        self.tools = [self._build_tool(raw) for raw in raw_tools]
        return list(self.tools)

    async def list_tools(self) -> list[MCPTool]:
        if not self.tools:
            await self.refresh_tools()
        return list(self.tools)

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        try:
            result = await self._request("tools/call", {"name": name, "arguments": arguments or {}})
        except MCPProtocolError as exc:
            raise MCPToolError(f"MCP tool {name!r} failed") from exc
        return _result_to_text(result)

    def as_langchain_tools(self) -> list[dict[str, Any]]:
        """Return provider-neutral tool descriptors accepted by orchestration."""

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "server": tool.server_name,
            }
            for tool in self.tools
        ]

    async def close(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None
        process, self._process = self._process, None
        if process is not None and process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except TimeoutError:
                process.kill()
                await process.wait()
        self.tools.clear()

    async def _connect_stdio(self) -> None:
        assert self.config.command is not None
        environment = os.environ.copy()
        environment.update(self.config.env)
        try:
            self._process = await asyncio.create_subprocess_exec(
                self.config.command,
                *self.config.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=environment,
            )
        except OSError as exc:
            raise MCPConnectionError(f"could not start MCP command: {self.config.command}") from exc

    async def _request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self._request_id += 1
        request_id = self._request_id
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        if self.config.transport == "stdio":
            response = await self._stdio_request(payload)
        else:
            response = await self._http_request(payload)
        if response.get("id") not in {request_id, None}:
            raise MCPProtocolError(
                f"response id {response.get('id')!r} does not match request {request_id}"
            )
        if "error" in response:
            error = response["error"]
            message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            raise MCPProtocolError(message)
        if "result" not in response:
            raise MCPProtocolError("JSON-RPC response has no result")
        return response["result"]

    async def _stdio_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        process = self._process
        if process is None or process.stdin is None or process.stdout is None:
            raise MCPConnectionError("stdio MCP client is not connected")
        async with self._io_lock:
            process.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode())
            try:
                await asyncio.wait_for(process.stdin.drain(), self.config.timeout)
                line = await asyncio.wait_for(process.stdout.readline(), self.config.timeout)
            except TimeoutError as exc:
                raise MCPProtocolError(f"MCP request {payload['method']!r} timed out") from exc
        if not line:
            error_text = ""
            if process.stderr is not None:
                with suppress(TimeoutError):
                    error_text = (
                        (await asyncio.wait_for(process.stderr.read(), 0.1)).decode().strip()
                    )
            raise MCPConnectionError(f"MCP server closed stdout: {error_text}")
        return _decode_response(line.decode())

    async def _http_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._http is None:
            raise MCPConnectionError("HTTP MCP client is not connected")
        try:
            response = await self._http.post("", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MCPConnectionError("MCP HTTP request failed") from exc
        data = response.json()
        if not isinstance(data, dict):
            raise MCPProtocolError("MCP HTTP response must be an object")
        return data

    def _build_tool(self, raw: Any) -> MCPTool:
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
            raise MCPProtocolError("invalid tool descriptor")
        name = raw["name"]

        async def caller(arguments: dict[str, Any]) -> str:
            return await self.call_tool(name, arguments)

        return MCPTool(
            name=name,
            description=str(raw.get("description", "")),
            parameters=dict(raw.get("inputSchema", {})),
            server_name=self.config.name,
            _caller=caller,
        )


def _decode_response(value: str) -> dict[str, Any]:
    try:
        response = json.loads(value)
    except json.JSONDecodeError as exc:
        raise MCPProtocolError("MCP server returned invalid JSON") from exc
    if not isinstance(response, dict):
        raise MCPProtocolError("MCP response must be an object")
    return response


def _result_to_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict) and isinstance(result.get("content"), list):
        chunks = []
        for item in result["content"]:
            if isinstance(item, dict) and item.get("type") == "text":
                chunks.append(str(item.get("text", "")))
        if chunks:
            return "\n".join(chunks)
    return json.dumps(result, ensure_ascii=False)
