"""
Defines the recurring/daily automated jobs. Each job simply invokes the
multi-agent LangGraph workflow with a preconfigured topic and stores the
result (via the Coordinator agent, which persists through MCP).
"""
from datetime import datetime

from app.config import settings
from app.utils.logger import get_logger
from app.workflows.graph_builder import run_workflow

logger = get_logger(__name__)


async def daily_research_digest_job():
    """Runs the full multi-agent workflow on a configured topic every day."""
    topic = settings.daily_task_topic
    logger.info(f"[{datetime.now().isoformat()}] Running daily research digest for: {topic}")
    try:
        result = await run_workflow(topic=topic, max_revisions=2)
        logger.info(f"Daily digest completed. Status: {result.get('status')}")
        return result
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Daily digest job failed: {exc}")
        raise
