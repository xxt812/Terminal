from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Default LLM provider selection."""

    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    default_provider: Literal["anthropic", "openai", "google", "faux"] = "faux"
    default_model: str = "faux-model"


class AnthropicSettings(BaseSettings):
    """Anthropic provider settings."""

    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_", env_file=".env", extra="ignore")

    api_key: SecretStr | None = None
    timeout: int = Field(default=60, gt=0)


class OpenAISettings(BaseSettings):
    """OpenAI provider settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=".env", extra="ignore")

    api_key: SecretStr | None = None
    timeout: int = Field(default=60, gt=0)


class ChromaSettings(BaseSettings):
    """Long-term memory storage settings."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_", env_file=".env", extra="ignore")

    persist_dir: Path = Path("./data/chroma")


class AgentSettings(BaseSettings):
    """Safety limits shared by all agent graphs."""

    model_config = SettingsConfigDict(env_prefix="AGENT_", env_file=".env", extra="ignore")

    tool_calls_budget: int = Field(default=20, ge=0)
    recursion_limit: int = Field(default=50, gt=0)


class Settings(BaseSettings):
    """Validated process-wide configuration root."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    llm: LLMSettings = Field(default_factory=LLMSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)

    sqlite_db_path: Path = Path("./data/app.db")
    checkpoint_db_path: Path = Path("./data/checkpoints.db")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["text", "json"] = "text"
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    dashboard_port: int = Field(default=8501, ge=1, le=65535)
    skill_dirs: Annotated[list[Path], NoDecode] = Field(default_factory=lambda: [Path("./skills")])
    mcp_config_path: Path = Path("./config/mcp_servers.yaml")

    @field_validator("skill_dirs", mode="before")
    @classmethod
    def _split_skill_dirs(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        separator = ";" if ";" in value else os.pathsep
        return [Path(part).expanduser() for part in value.split(separator) if part.strip()]

    @field_validator("sqlite_db_path", "checkpoint_db_path", "mcp_config_path", mode="after")
    @classmethod
    def _expand_path(cls, value: Path) -> Path:
        return value.expanduser()


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()
