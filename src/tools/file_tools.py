from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.agent_core.message import ToolResult
from src.tools.base import WorkspaceTool

DEFAULT_IGNORES = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}


class ReadTool(WorkspaceTool):
    name = "read"
    description = "Read a UTF-8 text file inside the workspace."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.resolve_path(_path_argument(arguments), must_exist=True)
        if not path.is_file():
            raise IsADirectoryError(path)
        content = path.read_text(encoding=str(arguments.get("encoding", "utf-8")))
        start = _positive_int(arguments.get("start_line", 1), "start_line")
        end_value = arguments.get("end_line")
        if start != 1 or end_value is not None:
            lines = content.splitlines(keepends=True)
            end = len(lines) if end_value is None else _positive_int(end_value, "end_line")
            if end < start:
                raise ValueError("end_line cannot be less than start_line")
            content = "".join(lines[start - 1 : end])
        return _result(self.name, content)


class WriteTool(WorkspaceTool):
    name = "write"
    description = "Write or append UTF-8 text inside the workspace."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.resolve_path(_path_argument(arguments))
        mode = str(arguments.get("mode", "overwrite"))
        if mode not in {"overwrite", "append", "create"}:
            raise ValueError("mode must be overwrite, append, or create")
        if mode == "create" and path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = str(arguments.get("content", ""))
        with path.open("a" if mode == "append" else "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        return _result(
            self.name, f"wrote {len(content)} characters to {path.relative_to(self.root_dir)}"
        )


class EditTool(WorkspaceTool):
    name = "edit"
    description = "Replace one exact text occurrence in a workspace file."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.resolve_path(_path_argument(arguments), must_exist=True)
        old = str(arguments.get("old_text", arguments.get("old", "")))
        new = str(arguments.get("new_text", arguments.get("new", "")))
        if not old:
            raise ValueError("old_text cannot be empty")
        content = path.read_text(encoding="utf-8")
        matches = content.count(old)
        if matches == 0:
            raise ValueError("old_text was not found")
        if matches > 1:
            raise ValueError(f"old_text must be unique; found {matches} matches")
        path.write_text(content.replace(old, new, 1), encoding="utf-8", newline="")
        return _result(self.name, f"edited {path.relative_to(self.root_dir)}")


class ListTool(WorkspaceTool):
    name = "ls"
    description = "List a directory inside the workspace."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.resolve_path(arguments.get("path", "."), must_exist=True)
        if not path.is_dir():
            raise NotADirectoryError(path)
        entries = sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        content = "\n".join(f"{'d' if item.is_dir() else 'f'} {item.name}" for item in entries)
        return _result(self.name, content)


class FindTool(WorkspaceTool):
    name = "find"
    description = "Find workspace files by glob pattern."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        base = self.resolve_path(arguments.get("path", "."), must_exist=True)
        pattern = str(arguments.get("pattern", arguments.get("glob", "*")))
        max_results = _positive_int(arguments.get("max_results", 200), "max_results")
        matches: list[str] = []
        for path in base.rglob("*"):
            if _is_ignored(path, self.root_dir) or not path.is_file():
                continue
            relative = path.relative_to(self.root_dir).as_posix()
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(relative, pattern):
                matches.append(relative)
                if len(matches) >= max_results:
                    break
        return _result(self.name, "\n".join(sorted(matches)))


class GrepTool(WorkspaceTool):
    name = "grep"
    description = "Search UTF-8 workspace files with a regular expression."

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        base = self.resolve_path(arguments.get("path", "."), must_exist=True)
        pattern = str(arguments.get("pattern", ""))
        if not pattern:
            raise ValueError("pattern cannot be empty")
        flags = 0 if arguments.get("case_sensitive", True) else re.IGNORECASE
        expression = re.compile(pattern, flags)
        glob = str(arguments.get("glob", "*"))
        context = int(arguments.get("context", 0))
        if context < 0:
            raise ValueError("context cannot be negative")
        max_results = _positive_int(arguments.get("max_results", 200), "max_results")
        files = [base] if base.is_file() else base.rglob("*")
        output: list[str] = []
        for path in files:
            if not path.is_file() or _is_ignored(path, self.root_dir):
                continue
            relative = path.relative_to(self.root_dir).as_posix()
            if not (fnmatch.fnmatch(path.name, glob) or fnmatch.fnmatch(relative, glob)):
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for index, line in enumerate(lines):
                if not expression.search(line):
                    continue
                start = max(0, index - context)
                end = min(len(lines), index + context + 1)
                output.extend(
                    f"{relative}:{number + 1}:{lines[number]}" for number in range(start, end)
                )
                if len(output) >= max_results:
                    return _result(self.name, "\n".join(output[:max_results]))
        return _result(self.name, "\n".join(output))


def _path_argument(arguments: dict[str, Any]) -> str | Path:
    value = arguments.get("file_path", arguments.get("path"))
    if not isinstance(value, (str, Path)) or not str(value):
        raise ValueError("file_path is required")
    return value


def _positive_int(value: Any, name: str) -> int:
    result = int(value)
    if result < 1:
        raise ValueError(f"{name} must be positive")
    return result


def _is_ignored(path: Path, root: Path) -> bool:
    return any(part in DEFAULT_IGNORES for part in path.relative_to(root).parts)


def _result(name: str, content: str) -> ToolResult:
    return ToolResult(call_id=f"builtin_{uuid4().hex[:12]}", name=name, content=content)
