"""
Builds the LangGraph state graph wiring together the Researcher, Writer,
Reviewer, and Coordinator agents into a multi-agent workflow with a
revise loop (Writer <-> Reviewer, bounded by max_revisions).

Graph shape:

    START -> researcher -> writer -> reviewer --(approved)--> coordinator -> END
                               ^                    |
                               |__(revise, budget left)_|
"""
from langgraph.graph import StateGraph, END

from app.agents.coordinator import CoordinatorAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.writer_agent import WriterAgent
from app.utils.logger import get_logger
from app.workflows.state import WorkflowState

logger = get_logger(__name__)

researcher = ResearcherAgent()
writer = WriterAgent()
reviewer = ReviewerAgent()
coordinator = CoordinatorAgent()


async def researcher_node(state: WorkflowState) -> dict:
    return await researcher.run(state)


async def writer_node(state: WorkflowState) -> dict:
    return await writer.run(state)


async def reviewer_node(state: WorkflowState) -> dict:
    return await reviewer.run(state)


async def coordinator_node(state: WorkflowState) -> dict:
    return await coordinator.run(state)


def route_after_review(state: WorkflowState) -> str:
    """Conditional edge: loop back to writer if revision needed & budget left,
    otherwise proceed to coordinator."""
    if state.get("approved"):
        return "coordinator"

    max_revisions = state.get("max_revisions", 2)
    if state.get("revision_count", 0) >= max_revisions:
        logger.info("Max revisions reached; forcing finalization.")
        return "coordinator"

    return "writer"


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("coordinator", coordinator_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"writer": "writer", "coordinator": "coordinator"},
    )
    graph.add_edge("coordinator", END)

    return graph.compile()


# Compiled, ready-to-invoke workflow graph (singleton)
workflow_app = build_workflow_graph()


async def run_workflow(topic: str, max_revisions: int = 2) -> dict:
    """Entry point used by the API layer / scheduler to execute the workflow."""
    initial_state: WorkflowState = {
        "topic": topic,
        "max_revisions": max_revisions,
        "revision_count": 0,
        "status": "started",
    }
    logger.info(f"Starting workflow for topic: {topic!r}")
    final_state = await workflow_app.ainvoke(initial_state)
    logger.info(f"Workflow finished with status: {final_state.get('status')}")
    return final_state
