"""
Writer agent: drafts (or revises) content based on research notes and,
on later passes, reviewer feedback.
"""
from app.agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    name = "writer"
    system_prompt = (
        "You are a skilled technical writer. Write clear, well-structured "
        "content (3-5 short paragraphs) based on the given research notes. "
        "If revision feedback is provided, address every point precisely."
    )

    async def run(self, state: dict) -> dict:
        topic = state["topic"]
        notes = state.get("research_notes", "")
        feedback = state.get("review_feedback")

        if feedback:
            self.logger.info("Revising draft based on reviewer feedback...")
            prompt = (
                f"Topic: {topic}\n\nResearch notes:\n{notes}\n\n"
                f"Previous draft:\n{state.get('draft', '')}\n\n"
                f"Reviewer feedback to address:\n{feedback}\n\n"
                "Write an improved draft that fully addresses the feedback."
            )
        else:
            self.logger.info("Writing initial draft...")
            prompt = f"Topic: {topic}\n\nResearch notes:\n{notes}\n\nWrite the draft."

        draft = await self._ask(prompt)
        return {"draft": draft, "status": "drafted"}
