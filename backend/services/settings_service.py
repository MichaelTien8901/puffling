import json

from sqlalchemy.orm import Session

from backend.models.settings import Settings


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: str) -> dict:
        rows = self.db.query(Settings).filter(Settings.user_id == user_id).all()
        return {r.key: json.loads(r.value) for r in rows}

    def get(self, user_id: str, key: str) -> object | None:
        row = self.db.query(Settings).filter(
            Settings.user_id == user_id, Settings.key == key
        ).first()
        return json.loads(row.value) if row else None

    def set(self, user_id: str, key: str, value: object) -> None:
        row = self.db.query(Settings).filter(
            Settings.user_id == user_id, Settings.key == key
        ).first()
        if row:
            row.value = json.dumps(value)
        else:
            self.db.add(Settings(user_id=user_id, key=key, value=json.dumps(value)))
        self.db.commit()

    def delete(self, user_id: str, key: str) -> bool:
        row = self.db.query(Settings).filter(
            Settings.user_id == user_id, Settings.key == key
        ).first()
        if row:
            self.db.delete(row)
            self.db.commit()
            return True
        return False
