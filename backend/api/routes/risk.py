from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.risk_service import RiskService

router = APIRouter()
service = RiskService()


class PositionSizeRequest(BaseModel):
    method: str
    params: dict = {}


class PortfolioRiskRequest(BaseModel):
    symbols: list[str]
    weights: list[float]
    start: str
    end: str


@router.post("/position-size")
def position_size(req: PositionSizeRequest):
    return service.position_size(req.method, **req.params)


@router.post("/portfolio")
def portfolio_risk(req: PortfolioRiskRequest):
    return service.portfolio_risk(req.symbols, req.weights, req.start, req.end)
