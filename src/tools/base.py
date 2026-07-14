from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from src.agent_core.message import ToolResult


class Tool(Protocol):
    name: str
    description: str

    def invoke(self, arguments: dict[str, Any]) -> ToolResult: ...


class WorkspaceTool:
    """Base for tools restricted to a single workspace root."""

    name = "workspace_tool"
    description = ""

    def __init__(self, root_dir: str | Path = ".") -> None:
        self.root_dir = Path(root_dir).expanduser().resolve()
        if not self.root_dir.is_dir():
            raise NotADirectoryError(self.root_dir)

    def resolve_path(self, value: str | Path, *, must_exist: bool = False) -> Path:
        raw = Path(value).expanduser()
        candidate = raw.resolve() if raw.is_absolute() else (self.root_dir / raw).resolve()
        try:
            candidate.relative_to(self.root_dir)
        except ValueError as exc:
            raise PermissionError(f"path escapes workspace: {value}") from exc
        if must_exist and not candidate.exists():
            raise FileNotFoundError(candidate)
        return candidate
