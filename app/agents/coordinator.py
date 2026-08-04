"""
Coordinator agent: finalizes the workflow once the draft is approved
(or the max revision count is hit), persists the result via MCP, and
sets the terminal status.
"""
from app.agents.base_agent import BaseAgent
from app.mcp.mcp_client import call_mcp_tool


class CoordinatorAgent(BaseAgent):
    name = "coordinator"
    system_prompt = "You are a workflow coordinator finalizing agent output."

    async def run(self, state: dict) -> dict:
        topic = state["topic"]
        draft = state.get("draft", "")

        await call_mcp_tool("save_note", {"key": f"final::{topic[:40]}", "content": draft})

        self.logger.info(f"Workflow complete for topic: {topic}")
        return {"final_output": draft, "status": "completed"}
