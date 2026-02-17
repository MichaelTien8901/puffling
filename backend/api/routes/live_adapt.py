import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.live_adapter_service import LiveAdapterService
from backend.services.scheduler_service import SchedulerService

router = APIRouter()


class CreateAdaptationRequest(BaseModel):
    strategy_id: int
    schedule: str  # cron expression, e.g. "0 2 * * SAT"
    trailing_window: int = 504
    max_param_change_pct: float = 25.0
    cooldown_days: int = 7
    confirmation_mode: str = "auto"
    vol_ratio_high: float = 1.5
    vol_ratio_low: float = 0.5


@router.post("/live")
def create_adaptation(
    req: CreateAdaptationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = LiveAdapterService(db)
    config = svc.create_config(
        user_id=user.id,
        strategy_id=req.strategy_id,
        schedule=req.schedule,
        trailing_window=req.trailing_window,
        max_param_change_pct=req.max_param_change_pct,
        cooldown_days=req.cooldown_days,
        confirmation_mode=req.confirmation_mode,
        vol_ratio_high=req.vol_ratio_high,
        vol_ratio_low=req.vol_ratio_low,
    )

    # Register with scheduler
    scheduler_svc = SchedulerService(db)
    scheduler_svc.register_adaptation(config)

    return {
        "id": config.id,
        "status": config.status,
        "schedule": config.schedule,
        "strategy_id": config.strategy_id,
    }


@router.get("/live")
def list_adaptations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = LiveAdapterService(db)
    scheduler_svc = SchedulerService(db)
    configs = svc.list_configs(user.id)
    result = []
    for c in configs:
        next_run = scheduler_svc.get_adaptation_next_run(c.id)
        result.append({
            "id": c.id,
            "strategy_id": c.strategy_id,
            "schedule": c.schedule,
            "trailing_window": c.trailing_window,
            "max_param_change_pct": c.max_param_change_pct,
            "cooldown_days": c.cooldown_days,
            "confirmation_mode": c.confirmation_mode,
            "status": c.status,
            "next_run": next_run,
            "created_at": str(c.created_at),
        })
    return result


@router.delete("/live/{config_id}")
def stop_adaptation(
    config_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = LiveAdapterService(db)
    if not svc.stop_config(config_id, user.id):
        raise HTTPException(status_code=404, detail="Adaptation config not found")

    # Remove from scheduler
    scheduler_svc = SchedulerService(db)
    scheduler_svc.unregister_adaptation(config_id)

    return {"status": "stopped"}


@router.get("/live/{config_id}/history")
def get_adaptation_history(
    config_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = LiveAdapterService(db)
    # Verify ownership
    config = svc.get_config(config_id, user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Adaptation config not found")

    events = svc.get_adaptation_history(config_id)
    return [
        {
            "id": e.id,
            "trigger_type": e.trigger_type,
            "regime_type": e.regime_type,
            "proposed_params": json.loads(e.proposed_params) if e.proposed_params else None,
            "applied_params": json.loads(e.applied_params) if e.applied_params else None,
            "was_capped": e.was_capped,
            "status": e.status,
            "reason": e.reason,
            "created_at": str(e.created_at),
        }
        for e in events
    ]
