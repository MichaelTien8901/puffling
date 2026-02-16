from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.factors_service import FactorsService

router = APIRouter()
service = FactorsService()


class ComputeRequest(BaseModel):
    symbols: list[str]
    start: str
    end: str
    factor_types: list[str] | None = None


class RiskFactorsRequest(BaseModel):
    symbols: list[str]
    start: str
    end: str
    n_components: int = 5


class ClusterRequest(BaseModel):
    symbols: list[str]
    start: str
    end: str
    method: str = "kmeans"


@router.post("/compute")
def compute_factors(req: ComputeRequest):
    return service.compute(req.symbols, req.start, req.end, req.factor_types)


@router.get("/library")
def get_library():
    return service.get_library()


@router.post("/risk-factors")
def risk_factors(req: RiskFactorsRequest):
    return service.risk_factors(req.symbols, req.start, req.end, req.n_components)


@router.post("/cluster")
def cluster_assets(req: ClusterRequest):
    return service.cluster_assets(req.symbols, req.start, req.end, req.method)
