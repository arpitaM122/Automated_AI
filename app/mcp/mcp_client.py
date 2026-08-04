"""
MCP client helper - simplified version that mocks tool calls locally.
In production, this would connect to a real MCP server over stdio.
"""
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Simplified MCP tool caller that works offline.
    Returns mock data locally; can be swapped for real MCP server.
    """
    if tool_name == "web_search":
        query = arguments.get("query", "")
        return (
            f"[Mock web search for: '{query}']\n"
            f"- Key finding 1 on '{query}'\n"
            f"- Key finding 2 on '{query}'\n"
            f"- Key finding 3 on '{query}'\n"
            "(Note: Replace this with real search API for live results)"
        )
    elif tool_name == "save_note":
        key = arguments.get("key", "")
        return f"Note '{key}' saved locally."
    elif tool_name == "read_notes":
        return "No notes saved yet."
    else:
        return f"Unknown tool: {tool_name}"


async def is_mcp_reachable() -> bool:
    """In simplified mode, MCP is always 'reachable' (we use mocks)."""
    return True
