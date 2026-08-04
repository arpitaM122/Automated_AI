"""
Pydantic request/response models for the API layer.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowRunRequest(BaseModel):
    topic: str = Field(..., description="Topic/task the multi-agent workflow should process")
    max_revisions: int = Field(2, ge=0, le=5, description="Max writer<->reviewer revision loops")


class WorkflowRunResponse(BaseModel):
    run_id: str
    status: str
    topic: str
    research_notes: Optional[str] = None
    draft: Optional[str] = None
    review_feedback: Optional[str] = None
    revision_count: int = 0
    final_output: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class WorkflowStatusResponse(BaseModel):
    run_id: str
    status: str


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    ollama_model: str
    mcp_reachable: bool


class DailyTaskConfig(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    topic: str
