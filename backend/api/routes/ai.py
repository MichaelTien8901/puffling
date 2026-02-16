from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.ai_service import AIService

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class SentimentRequest(BaseModel):
    text: str


class TopicsRequest(BaseModel):
    documents: list[str]
    n_topics: int = 5


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AIService(db)
    return svc.chat(user.id, req.message, req.conversation_id)


@router.post("/sentiment")
def sentiment(req: SentimentRequest, db: Session = Depends(get_db)):
    svc = AIService(db)
    return svc.analyze_sentiment(req.text)


@router.post("/topics")
def topics(req: TopicsRequest, db: Session = Depends(get_db)):
    svc = AIService(db)
    return svc.extract_topics(req.documents, req.n_topics)


@router.get("/conversations")
def conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AIService(db)
    convs = svc.get_conversations(user.id)
    return [{"id": c.id, "created_at": str(c.created_at)} for c in convs]
