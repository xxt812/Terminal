"""Project exception hierarchy."""


class TCAError(Exception):
    """Base class for all expected application errors."""


class ConfigError(TCAError):
    """Configuration is missing or invalid."""


class AgentError(TCAError):
    """Agent execution or graph construction failed."""


class AgentGraphError(AgentError):
    """Agent graph topology or routing is invalid."""


class LLMProviderError(TCAError):
    """An LLM provider could not be created or invoked."""


class ToolExecutionError(TCAError):
    """A built-in or external tool failed to execute."""


class MCPError(TCAError):
    """Base class for MCP client failures."""


class MCPConnectionError(MCPError):
    """An MCP transport could not be connected."""


class MCPProtocolError(MCPError):
    """An MCP peer returned an invalid JSON-RPC response."""


class MCPToolError(MCPError):
    """An MCP tool invocation failed."""
