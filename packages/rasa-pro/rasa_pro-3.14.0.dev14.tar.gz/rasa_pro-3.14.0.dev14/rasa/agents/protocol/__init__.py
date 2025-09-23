# Import agents conditionally based on available dependencies
__all__ = []

try:
    from rasa.agents.protocol.a2a.a2a_agent import A2AAgent
    __all__.append("A2AAgent")
except ImportError:
    A2AAgent = None

# MCP is always available (in default dependencies)
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.protocol.mcp.mcp_task_agent import MCPTaskAgent
__all__.extend(["MCPOpenAgent", "MCPTaskAgent"])
