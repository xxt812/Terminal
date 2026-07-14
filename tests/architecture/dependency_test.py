import pytest
from importlib import import_module

def test_dependency_rules():
    # 1. 检查 config 是否仅依赖基础库
    config_mod = import_module("src.config.config_loader")
    for name in dir(config_mod):
        if name.startswith("__"):
            continue
        obj = getattr(config_mod, name)
        if hasattr(obj, "__module__") and "src" in obj.__module__:
            if "config" not in obj.__module__:
                pytest.fail(f"config module {name} depends on {obj.__module__}!")

    # 2. 检查 agent_core 是否仅依赖 config
    agent_mod = import_module("src.agent_core.agent")
    for name in dir(agent_mod):
        if name.startswith("__"):
            continue
        obj = getattr(agent_mod, name)
        if hasattr(obj, "__module__") and "src" in obj.__module__:
            if "agent_core" not in obj.__module__ and "config" not in obj.__module__:
                pytest.fail(f"agent_core {name} depends on {obj.__module__}!")
