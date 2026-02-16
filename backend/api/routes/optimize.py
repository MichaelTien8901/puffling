import json
import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db, SessionLocal
from backend.core.deps import get_current_user
from backend.models.optimization_job import OptimizationJob
from backend.models.user import User
from backend.services.optimizer_service import OptimizerService

router = APIRouter()


class StrategyOptimizeRequest(BaseModel):
    strategy_type: str
    symbols: list[str]
    start: str
    end: str
    param_grid: dict | None = None
    n_splits: int = 5
    train_ratio: float = 0.7


class ModelTuneRequest(BaseModel):
    model_type: str
    symbols: list[str]
    start: str
    end: str
    param_grid: dict | None = None


def _run_strategy_optimization(job_id: int, user_id: str, req: StrategyOptimizeRequest):
    db = SessionLocal()
    try:
        svc = OptimizerService(db)
        svc.run_strategy_optimization(
            job_id=job_id,
            user_id=user_id,
            strategy_type=req.strategy_type,
            symbols=req.symbols,
            start=req.start,
            end=req.end,
            param_grid=req.param_grid,
            n_splits=req.n_splits,
            train_ratio=req.train_ratio,
        )
    except Exception:
        pass  # Error status already set in service
    finally:
        db.close()


def _run_model_tuning(job_id: int, user_id: str, req: ModelTuneRequest):
    db = SessionLocal()
    try:
        svc = OptimizerService(db)
        svc.run_model_tuning(
            job_id=job_id,
            user_id=user_id,
            model_type=req.model_type,
            symbols=req.symbols,
            start=req.start,
            end=req.end,
            param_grid=req.param_grid,
        )
    except Exception:
        pass
    finally:
        db.close()


@router.post("/strategy")
def submit_strategy_optimization(
    req: StrategyOptimizeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Validate grid size before creating job
    svc = OptimizerService(db)
    grid = req.param_grid or svc.get_default_grid(req.strategy_type)
    try:
        total = svc.validate_grid_size(grid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    job = OptimizationJob(
        user_id=user.id,
        job_type="strategy",
        strategy_type=req.strategy_type,
        config=json.dumps({
            "symbols": req.symbols,
            "start": req.start,
            "end": req.end,
            "param_grid": grid,
            "n_splits": req.n_splits,
            "train_ratio": req.train_ratio,
        }),
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Run in background thread
    thread = threading.Thread(
        target=_run_strategy_optimization,
        args=(job.id, user.id, req),
        daemon=True,
    )
    thread.start()

    return {"job_id": job.id, "status": "running", "total_combinations": total}


@router.post("/model")
def submit_model_tuning(
    req: ModelTuneRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = OptimizationJob(
        user_id=user.id,
        job_type="model",
        strategy_type=req.model_type,
        config=json.dumps({
            "symbols": req.symbols,
            "start": req.start,
            "end": req.end,
            "param_grid": req.param_grid,
        }),
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    thread = threading.Thread(
        target=_run_model_tuning,
        args=(job.id, user.id, req),
        daemon=True,
    )
    thread.start()

    return {"job_id": job.id, "status": "running"}


@router.get("/")
def list_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = OptimizerService(db)
    jobs = svc.list_jobs(user.id)
    result = []
    for j in jobs:
        best_sharpe = None
        if j.results:
            try:
                parsed = json.loads(j.results)
                if isinstance(parsed, list) and parsed:
                    best_sharpe = parsed[0].get("mean_sharpe")
            except (json.JSONDecodeError, KeyError):
                pass
        result.append({
            "id": j.id,
            "job_type": j.job_type,
            "strategy_type": j.strategy_type,
            "status": j.status,
            "created_at": str(j.created_at),
            "best_sharpe": best_sharpe,
        })
    return result


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = OptimizerService(db)
    job = svc.get_job(job_id, user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "id": job.id,
        "job_type": job.job_type,
        "strategy_type": job.strategy_type,
        "status": job.status,
        "config": json.loads(job.config),
        "created_at": str(job.created_at),
    }
    if job.results:
        try:
            response["results"] = json.loads(job.results)
            if isinstance(response["results"], list) and response["results"]:
                response["best_params"] = response["results"][0].get("params")
        except json.JSONDecodeError:
            response["results"] = None
    return response


@router.delete("/{job_id}")
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = OptimizerService(db)
    job = svc.get_job(job_id, user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    svc.cancel_job(job_id)
    return {"status": "cancelled"}
