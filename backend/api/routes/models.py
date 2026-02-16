from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.model_service import ModelService

router = APIRouter()
service = ModelService()


class TrainRequest(BaseModel):
    model_type: str
    params: dict = {}


class PredictRequest(BaseModel):
    model_type: str
    params: dict = {}


@router.get("/types")
def list_types():
    return service.list_types()


@router.post("/train")
def train(req: TrainRequest):
    return service.train(req.model_type, req.params)


@router.post("/predict")
def predict(req: PredictRequest):
    return service.predict(req.model_type, req.params)
