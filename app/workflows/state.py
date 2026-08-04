"""
Shared state schema passed between LangGraph nodes.
"""
from typing import Optional, TypedDict


class WorkflowState(TypedDict, total=False):
    topic: str
    max_revisions: int
    research_notes: Optional[str]
    draft: Optional[str]
    review_feedback: Optional[str]
    approved: bool
    revision_count: int
    final_output: Optional[str]
    status: str
