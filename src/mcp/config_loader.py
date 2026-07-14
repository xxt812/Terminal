from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.exceptions import ConfigError


class MCPServerConfig(BaseModel):
    """Validated connection settings for one MCP server."""

    model_config = ConfigDict(extra="forbid")

    name: str
    transport: Literal["stdio", "sse", "http"] = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    env: dict[str, str] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, gt=0)

    @model_validator(mode="after")
    def _validate_transport_fields(self) -> MCPServerConfig:
        if self.transport == "stdio" and not self.command:
            raise ValueError("stdio transport requires command")
        if self.transport in {"sse", "http"} and not self.url:
            raise ValueError(f"{self.transport} transport requires url")
        return self


def load_server_configs(path: str | Path) -> dict[str, MCPServerConfig]:
    """Load `mcpServers` from YAML without starting any processes."""

    source = Path(path).expanduser()
    if not source.is_file():
        raise ConfigError(f"MCP config file not found: {source}")
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid MCP YAML: {source}") from exc
    raw_servers: Any = document.get("mcpServers", document.get("servers", {}))
    if not isinstance(raw_servers, dict):
        raise ConfigError("MCP config must contain a mapping named mcpServers")
    configs: dict[str, MCPServerConfig] = {}
    for name, values in raw_servers.items():
        if not isinstance(values, dict):
            raise ConfigError(f"MCP server {name!r} must be a mapping")
        configs[name] = MCPServerConfig(name=name, **values)
    return configs
