from typing import Protocol, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class AgentMessage:
    """统一消息格式，所有消息必须包含此结构"""
    content: str
    role: str  # 'user' / 'assistant' / 'system'
    metadata: dict = None


class BaseAgent(Protocol):
    """所有Agent实现必须继承此协议"""
    def process(self, message: AgentMessage) -> AgentMessage:
        """处理消息并返回响应，必须保持消息结构一致性"""
        ...

class BaseChatModel(Protocol):
    """所有LLM模型实现必须继承此协议"""
    def generate(self, prompt: str) -> str:
        """接收提示词，返回模型生成的文本"""
        ...

class MemoryBackend(Protocol):
    """所有记忆存储实现必须继承此协议"""
    def save(self, state: dict) -> None:
        """保存当前状态，无返回值"""
        ...
    def load(self, context: str) -> dict:
        """加载指定上下文的状态，返回字典"""
        ...
