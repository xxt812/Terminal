from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config.settings import Settings

pytestmark = pytest.mark.unit


def test_settings_have_safe_local_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.llm.default_provider == "faux"
    assert settings.agent.tool_calls_budget == 20
    assert settings.skill_dirs == [Path("skills")]


def test_settings_parse_skill_dirs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKILL_DIRS", "./skills;~/shared-skills")

    settings = Settings(_env_file=None)

    assert settings.skill_dirs[0] == Path("skills")
    assert settings.skill_dirs[1] == Path("~/shared-skills").expanduser()


def test_settings_reject_invalid_port() -> None:
    with pytest.raises(ValidationError):
        Settings(api_port=70_000, _env_file=None)
