"""
Basic tests for the workflow graph and API using mocked LLM/MCP calls
(no live Ollama or MCP server required to run these).
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.workflows.state import WorkflowState


@pytest.mark.asyncio
async def test_workflow_state_shape():
    state: WorkflowState = {
        "topic": "test topic",
        "max_revisions": 2,
        "revision_count": 0,
        "status": "started",
    }
    assert state["topic"] == "test topic"
    assert state["max_revisions"] == 2


@pytest.mark.asyncio
async def test_researcher_agent_run():
    from app.agents.researcher_agent import ResearcherAgent

    agent = ResearcherAgent()
    with patch("app.agents.researcher_agent.call_mcp_tool", new=AsyncMock(return_value="mocked search results")):
        with patch.object(agent, "_ask", new=AsyncMock(return_value="mocked research notes")):
            result = await agent.run({"topic": "local LLMs"})
    assert result["research_notes"] == "mocked research notes"
    assert result["status"] == "researched"


@pytest.mark.asyncio
async def test_writer_agent_initial_draft():
    from app.agents.writer_agent import WriterAgent

    agent = WriterAgent()
    with patch.object(agent, "_ask", new=AsyncMock(return_value="mocked draft")):
        result = await agent.run({"topic": "local LLMs", "research_notes": "notes"})
    assert result["draft"] == "mocked draft"
    assert result["status"] == "drafted"


@pytest.mark.asyncio
async def test_reviewer_agent_approves():
    from app.agents.reviewer_agent import ReviewerAgent

    agent = ReviewerAgent()
    with patch.object(agent, "_ask", new=AsyncMock(return_value="APPROVED")):
        result = await agent.run({"topic": "t", "research_notes": "n", "draft": "d"})
    assert result["approved"] is True
    assert result["review_feedback"] is None


@pytest.mark.asyncio
async def test_reviewer_agent_requests_revision():
    from app.agents.reviewer_agent import ReviewerAgent

    agent = ReviewerAgent()
    with patch.object(agent, "_ask", new=AsyncMock(return_value="REVISE: add more detail")):
        result = await agent.run({"topic": "t", "research_notes": "n", "draft": "d", "revision_count": 0})
    assert result["approved"] is False
    assert result["review_feedback"] == "add more detail"
    assert result["revision_count"] == 1


def test_route_after_review_approved():
    from app.workflows.graph_builder import route_after_review

    state = {"approved": True}
    assert route_after_review(state) == "coordinator"


def test_route_after_review_revise_within_budget():
    from app.workflows.graph_builder import route_after_review

    state = {"approved": False, "revision_count": 1, "max_revisions": 2}
    assert route_after_review(state) == "writer"


def test_route_after_review_budget_exhausted():
    from app.workflows.graph_builder import route_after_review

    state = {"approved": False, "revision_count": 2, "max_revisions": 2}
    assert route_after_review(state) == "coordinator"
