from fastapi import APIRouter

from backend.services.monitor_service import MonitorService

router = APIRouter()
service = MonitorService()


@router.get("/trades")
def get_trade_log():
    return service.get_trade_log()


@router.get("/pnl")
def get_pnl():
    return service.get_pnl()


@router.get("/health")
def get_health():
    return service.get_health()
