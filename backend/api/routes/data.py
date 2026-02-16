from fastapi import APIRouter

from backend.services.data_service import DataService

router = APIRouter()
service = DataService()


@router.get("/ohlcv")
def get_ohlcv(symbol: str, start: str, end: str, interval: str = "1d"):
    return service.get_ohlcv(symbol, start, end, interval)


@router.get("/symbols")
def get_symbols():
    return service.get_symbols()
