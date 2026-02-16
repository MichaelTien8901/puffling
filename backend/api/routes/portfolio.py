from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.portfolio_service import PortfolioService

router = APIRouter()
service = PortfolioService()


class OptimizeRequest(BaseModel):
    symbols: list[str]
    start: str
    end: str
    method: str = "mean_variance"


class TearsheetRequest(BaseModel):
    returns: list[float]


@router.post("/optimize")
def optimize(req: OptimizeRequest):
    return service.optimize(req.symbols, req.start, req.end, req.method)


@router.post("/tearsheet")
def tearsheet(req: TearsheetRequest):
    return service.tearsheet(req.returns)
