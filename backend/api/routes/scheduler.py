from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.scheduler_service import SchedulerService

router = APIRouter()


class CreateJobRequest(BaseModel):
    job_type: str
    schedule: str  # cron expression e.g. "0 9 * * 1-5"
    config: dict = {}


class UpdateJobRequest(BaseModel):
    schedule: str | None = None
    config: dict | None = None
    enabled: bool | None = None


@router.get("/")
def list_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SchedulerService(db)
    jobs = svc.get_jobs(user.id)
    return [
        {"id": j.id, "job_type": j.job_type, "schedule": j.schedule, "config": j.config, "enabled": j.enabled}
        for j in jobs
    ]


@router.post("/")
def create_job(req: CreateJobRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SchedulerService(db)
    job = svc.create_job(user.id, req.job_type, req.schedule, req.config)
    return {"id": job.id, "job_type": job.job_type, "schedule": job.schedule}


@router.put("/{job_id}")
def update_job(job_id: int, req: UpdateJobRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SchedulerService(db)
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    job = svc.update_job(job_id, user.id, **updates)
    if job:
        return {"id": job.id, "enabled": job.enabled}
    return {"error": "not found"}


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SchedulerService(db)
    if svc.delete_job(job_id, user.id):
        return {"status": "deleted"}
    return {"error": "not found"}


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    svc = SchedulerService(db)
    return svc.get_status()
