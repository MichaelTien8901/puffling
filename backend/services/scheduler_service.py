import json
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from backend.models.scheduled_job import ScheduledJob

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


class SchedulerService:
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = get_scheduler()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            self._load_jobs()

    def _load_jobs(self):
        jobs = self.db.query(ScheduledJob).filter(ScheduledJob.enabled.is_(True)).all()
        for job in jobs:
            self._add_job_to_scheduler(job)
        logger.info(f"Loaded {len(jobs)} scheduled jobs")

    def _add_job_to_scheduler(self, job: ScheduledJob):
        job_id = f"job_{job.id}"
        config = json.loads(job.config)
        handler = _get_job_handler(job.job_type)
        if handler:
            try:
                self.scheduler.add_job(
                    handler,
                    trigger=CronTrigger.from_crontab(job.schedule),
                    id=job_id,
                    replace_existing=True,
                    kwargs={"config": config, "user_id": job.user_id},
                )
            except RuntimeError:
                pass  # Event loop closed (e.g., during tests)

    def create_job(self, user_id: str, job_type: str, schedule: str, config: dict) -> ScheduledJob:
        job = ScheduledJob(
            user_id=user_id, job_type=job_type,
            schedule=schedule, config=json.dumps(config), enabled=True,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        self._add_job_to_scheduler(job)
        return job

    def get_jobs(self, user_id: str) -> list[ScheduledJob]:
        return self.db.query(ScheduledJob).filter(ScheduledJob.user_id == user_id).all()

    def update_job(self, job_id: int, user_id: str, **kwargs) -> ScheduledJob | None:
        job = self.db.query(ScheduledJob).filter(
            ScheduledJob.id == job_id, ScheduledJob.user_id == user_id
        ).first()
        if not job:
            return None
        for key, value in kwargs.items():
            if key == "config":
                value = json.dumps(value)
            setattr(job, key, value)
        self.db.commit()
        self.db.refresh(job)
        # Update scheduler
        scheduler_id = f"job_{job.id}"
        if job.enabled:
            self._add_job_to_scheduler(job)
        else:
            try:
                self.scheduler.remove_job(scheduler_id)
            except Exception:
                pass
        return job

    def delete_job(self, job_id: int, user_id: str) -> bool:
        job = self.db.query(ScheduledJob).filter(
            ScheduledJob.id == job_id, ScheduledJob.user_id == user_id
        ).first()
        if not job:
            return False
        try:
            self.scheduler.remove_job(f"job_{job.id}")
        except Exception:
            pass
        self.db.delete(job)
        self.db.commit()
        return True

    def get_status(self) -> list[dict]:
        scheduler_jobs = self.scheduler.get_jobs()
        return [
            {"id": j.id, "next_run": str(j.next_run_time), "name": j.name}
            for j in scheduler_jobs
        ]


def _get_job_handler(job_type: str):
    handlers = {
        "market_scan": _run_market_scan,
        "portfolio_check": _run_portfolio_check,
        "ai_analysis": _run_ai_analysis,
        "alert_check": _run_alert_check,
    }
    return handlers.get(job_type)


async def _run_market_scan(config: dict, user_id: str):
    logger.info(f"Running market scan for user {user_id}: {config}")
    from backend.core.database import SessionLocal
    from backend.services.strategy_service import StrategyService
    db = SessionLocal()
    try:
        svc = StrategyService(db)
        result = svc.generate_signals(
            config["strategy_type"], config.get("params", {}),
            config["symbols"], config["start"], config["end"],
        )
        logger.info(f"Market scan complete: {len(result.get('signals', []))} signals")
    finally:
        db.close()


async def _run_portfolio_check(config: dict, user_id: str):
    logger.info(f"Running portfolio check for user {user_id}")


async def _run_ai_analysis(config: dict, user_id: str):
    logger.info(f"Running AI analysis for user {user_id}")


async def _run_alert_check(config: dict, user_id: str):
    logger.info(f"Running alert check for user {user_id}")
