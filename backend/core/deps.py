from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.models.user import User


def get_current_user(db: Session) -> User:
    user = db.query(User).filter(User.id == settings.default_user_id).first()
    if not user:
        user = User(id=settings.default_user_id, name="Default User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
