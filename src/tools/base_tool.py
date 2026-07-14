from typing import Any

class BaseTool:
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Subclasses must implement run method")
