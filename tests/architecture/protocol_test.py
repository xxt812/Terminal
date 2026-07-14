from src.agent_core.protocol import AgentMessage, BaseAgent


def test_protocol_definition():
    # 验证AgentMessage结构
    msg = AgentMessage(content="test", role="user", metadata={})
    assert msg.content == "test"

    # 验证协议继承
    class TestAgent(BaseAgent):
        def process(self, message: AgentMessage) -> AgentMessage:
            return message

    # 实例化测试
    agent = TestAgent()
    assert hasattr(agent, 'process')

    # 无错误即通过
    assert True
