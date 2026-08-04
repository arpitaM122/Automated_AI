"""
MCP (Model Context Protocol) server reference.

NOTE: This is a reference implementation. The actual app uses simplified
MCP client that mocks tool calls locally (see mcp_client.py).

If you want to use a real MCP server, install: pip install mcp
Then uncomment and use the code below.

Tool definitions:
  - web_search(query): Search the web for information
  - save_note(key, content): Persist a note to local disk
  - read_notes(): List all previously saved notes
"""
import json
from pathlib import Path

# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# from mcp.types import TextContent, Tool

NOTES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)


# Simplified local tool implementations (used by mcp_client.py)
def web_search(query: str) -> str:
    """Mock web search - replace with real API call."""
    return (
        f"[Mock search for: '{query}']\n"
        f"- Finding 1 related to '{query}'\n"
        f"- Finding 2 related to '{query}'\n"
        f"- Finding 3 related to '{query}'"
    )


def save_note(key: str, content: str) -> str:
    """Save a note to local JSON file."""
    path = NOTES_DIR / f"{key}.json"
    path.write_text(json.dumps({"key": key, "content": content}, indent=2))
    return f"Note '{key}' saved to {path}"


def read_notes() -> str:
    """Read all saved notes."""
    notes = []
    for f in NOTES_DIR.glob("*.json"):
        try:
            notes.append(json.loads(f.read_text()))
        except Exception:  # noqa: BLE001
            pass
    return json.dumps(notes, indent=2)


# Reference: Full MCP server implementation (uncomment if mcp library is installed)
# ============================================================================
# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# from mcp.types import TextContent, Tool
# 
# server = Server("ai-workflow-mcp-server")
# 
# @server.list_tools()
# async def list_tools() -> list[Tool]:
#     return [
#         Tool(name="web_search", description="Search the web...", inputSchema={...}),
#         Tool(name="save_note", description="Save a note...", inputSchema={...}),
#         Tool(name="read_notes", description="List notes...", inputSchema={...}),
#     ]
# 
# @server.call_tool()
# async def call_tool(name: str, arguments: dict) -> list[TextContent]:
#     if name == "web_search":
#         return [TextContent(type="text", text=web_search(arguments["query"]))]
#     elif name == "save_note":
#         return [TextContent(type="text", text=save_note(arguments["key"], arguments["content"]))]
#     elif name == "read_notes":
#         return [TextContent(type="text", text=read_notes())]
#     return [TextContent(type="text", text=f"Unknown tool: {name}")]
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(server.run())
