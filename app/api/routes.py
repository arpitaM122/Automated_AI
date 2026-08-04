"""
FastAPI route definitions for the workflow automation platform.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.automation.daily_tasks import daily_research_digest_job
from app.llm.ollama_client import ollama_client
from app.mcp.mcp_client import call_mcp_tool, is_mcp_reachable
from app.models.schemas import (
    HealthResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStatusResponse,
)
from app.utils.logger import get_logger
from app.workflows.graph_builder import run_workflow

logger = get_logger(__name__)
router = APIRouter()

# In-memory run store (swap for Redis/DB in production)
RUNS: dict[str, dict] = {}


@router.get("/health", response_model=HealthResponse)
async def health():
    ollama_ok = await ollama_client.is_reachable()
    mcp_ok = await is_mcp_reachable()  # Always True in simplified mode
    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama_reachable=ollama_ok,
        ollama_model=ollama_client.model,
        mcp_reachable=mcp_ok,
    )


@router.post("/workflow/run", response_model=WorkflowRunResponse)
async def trigger_workflow(payload: WorkflowRunRequest):
    run_id = str(uuid.uuid4())
    started_at = datetime.utcnow()

    RUNS[run_id] = {
        "run_id": run_id,
        "status": "running",
        "topic": payload.topic,
        "started_at": started_at,
    }

    try:
        result = await run_workflow(topic=payload.topic, max_revisions=payload.max_revisions)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Workflow run {run_id} failed: {exc}")
        RUNS[run_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    finished_at = datetime.utcnow()
    response = WorkflowRunResponse(
        run_id=run_id,
        status=result.get("status", "completed"),
        topic=payload.topic,
        research_notes=result.get("research_notes"),
        draft=result.get("draft"),
        review_feedback=result.get("review_feedback"),
        revision_count=result.get("revision_count", 0),
        final_output=result.get("final_output"),
        started_at=started_at,
        finished_at=finished_at,
    )
    RUNS[run_id] = response.model_dump()
    return response


@router.get("/workflow/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/workflow", response_model=list[WorkflowStatusResponse])
async def list_workflows():
    return [{"run_id": r["run_id"], "status": r["status"]} for r in RUNS.values()]


@router.post("/automation/run-daily-now")
async def run_daily_now(background_tasks: BackgroundTasks):
    """Manually trigger the daily automation job immediately (useful for testing)."""
    background_tasks.add_task(daily_research_digest_job)
    return {"message": "Daily task triggered in background."}


@router.post("/mcp/tool/{tool_name}")
async def invoke_mcp_tool(tool_name: str, arguments: dict):
    result = await call_mcp_tool(tool_name, arguments)
    return {"tool": tool_name, "result": result}
