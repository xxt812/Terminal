from .protocol import AgentMessage, BaseAgent

class Node:
    """流程节点抽象，所有节点必须实现"""
    def execute(self, message: AgentMessage) -> AgentMessage:
        """执行节点逻辑，返回下一条消息"""
        ...

class StateGraph:
    """状态图引擎，管理节点流"""
    def __init__(self, nodes: list[Node]):
        self.nodes = nodes

    def run(self, message: AgentMessage) -> AgentMessage:
        """按节点顺序执行流程"""
        for node in self.nodes:
            message = node.execute(message)
        return message

# 甲必须创建的示例Agent（实现BaseAgent协议）
class ExampleAgent(BaseAgent):
    def process(self, message: AgentMessage) -> AgentMessage:
        return AgentMessage(
            content="Hello from ExampleAgent",
            role="assistant",
            metadata={"source": "example"}
        )
