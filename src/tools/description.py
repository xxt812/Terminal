from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolDescription(BaseModel):
    """Provider-neutral description used for model tool registration."""

    name: str
    description: str
    parameters_schema: dict[str, Any] = Field(default_factory=dict)
    return_type: str = "string"
    examples: list[dict[str, Any]] = Field(default_factory=list)
