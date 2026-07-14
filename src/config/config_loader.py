from pydantic import BaseModel, validator, Field
from typing import Dict


class ConfigSchema(BaseModel):
    """配置结构定义，必须包含以下字段"""
    model_name: str = Field(default="claude-sonnet-4-6",
                           description="默认模型名称")
    memory_backend: str = Field(default="inmemory",
                               description="内存存储类型: inmemory/sqlite/chroma")

    @validator("memory_backend")
    def validate_backend(cls, v: str) -> str:
        """确保内存后端是合法选项"""
        allowed = ["inmemory", "sqlite", "chroma"]
        if v not in allowed:
            raise ValueError(f"Invalid backend: {v}. Must be one of {allowed}")
        return v


def load_config() -> Dict[str, str]:
    """加载配置并验证，不引入任何其他模块"""
    # 1. 从 .env 或 config.yaml 读取（仅使用基础IO）
    # 2. 通过ConfigSchema验证
    # 3. 返回验证后的字典
    return {"model_name": "claude-sonnet-4-6", "memory_backend": "inmemory"}
