"""
Reviewer agent: critiques the draft. Responds with either "APPROVED" or
"REVISE: <feedback>" so the graph's conditional edge can route accordingly.
"""
from app.agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    system_prompt = (
        "You are a strict but fair editor. Review the draft against the topic "
        "and research notes. If it is accurate, clear, and well-structured, "
        "respond with exactly: APPROVED. "
        "Otherwise respond with: REVISE: <specific, actionable feedback>."
    )

    async def run(self, state: dict) -> dict:
        topic = state["topic"]
        notes = state.get("research_notes", "")
        draft = state.get("draft", "")

        prompt = (
            f"Topic: {topic}\n\nResearch notes:\n{notes}\n\nDraft to review:\n{draft}\n\n"
            "Provide your verdict now."
        )
        verdict = await self._ask(prompt)
        self.logger.info(f"Reviewer verdict: {verdict[:80]}...")

        if verdict.strip().upper().startswith("APPROVED"):
            return {"review_feedback": None, "approved": True, "status": "approved"}

        feedback = verdict.split(":", 1)[1].strip() if ":" in verdict else verdict
        revision_count = state.get("revision_count", 0) + 1
        return {
            "review_feedback": feedback,
            "approved": False,
            "revision_count": revision_count,
            "status": "revision_requested",
        }
