from .base_tool import BaseTool

class ReadTool(BaseTool):
    def run(self, path: str) -> str:
        return f"Read contents of {path}"

class EditTool(BaseTool):
    def run(self, path: str, old: str, new: str) -> str:
        return f"Edited {path}: {old} → {new}"

class WriteTool(BaseTool):
    def run(self, path: str, content: str) -> str:
        return f"Wrote to {path}: {content}"

class GrepTool(BaseTool):
    def run(self, pattern: str, paths: list[str]) -> list[str]:
        return [f"Found match in {p}" for p in paths]

class FindTool(BaseTool):
    def run(self, pattern: str) -> list[str]:
        return [f"Found {pattern} in: ..."]

class LsTool(BaseTool):
    def run(self, path: str) -> list[str]:
        return [f"List of files in {path}: ..."]
