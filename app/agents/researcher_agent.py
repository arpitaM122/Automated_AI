"""
Researcher agent: gathers information about the workflow topic using the
MCP `web_search` tool, then asks the local LLM to synthesize concise notes.
"""
from app.agents.base_agent import BaseAgent
from app.mcp.mcp_client import call_mcp_tool


class ResearcherAgent(BaseAgent):
    name = "researcher"
    system_prompt = (
        "You are a meticulous research analyst. Given raw search snippets, "
        "synthesize 4-6 concise, factual bullet points that will be used by "
        "a writer to draft content. Do not add fluff or opinions."
    )

    async def run(self, state: dict) -> dict:
        topic = state["topic"]
        self.logger.info(f"Researching topic: {topic}")

        raw_search = await call_mcp_tool("web_search", {"query": topic})
        await call_mcp_tool("save_note", {"key": f"research::{topic[:40]}", "content": raw_search})

        prompt = (
            f"Topic: {topic}\n\n"
            f"Raw search snippets:\n{raw_search}\n\n"
            "Synthesize these into clear research notes for a writer."
        )
        notes = await self._ask(prompt)

        return {"research_notes": notes, "status": "researched"}
