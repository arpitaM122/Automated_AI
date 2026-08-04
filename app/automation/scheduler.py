"""
APScheduler wiring for automated daily tasks. Started from app.main on
FastAPI startup, stopped cleanly on shutdown.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.automation.daily_tasks import daily_research_digest_job
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler():
    trigger = CronTrigger(hour=settings.daily_task_hour, minute=settings.daily_task_minute)
    scheduler.add_job(
        daily_research_digest_job,
        trigger=trigger,
        id="daily_research_digest",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started. Daily digest will run at "
        f"{settings.daily_task_hour:02d}:{settings.daily_task_minute:02d}."
    )


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
