from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models.history import History
from ..schemas.history import HistoryCreate

class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_history(self, user_id: int, history_data: HistoryCreate) -> History:
        history = History(user_id=user_id, **history_data.model_dump())
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def get_history_by_id(self, history_id: int) -> Optional[History]:
        return self.db.query(History).options(
            joinedload(History.scenario)
        ).filter(History.id == history_id).first()
    
    def get_history_by_user_id(self, user_id: int, page: int = 1, size: int = 10):
        total = self.db.query(History).filter(History.user_id == user_id).count()
        history = (
            self.db.query(History)
            .options(joinedload(History.scenario))
            .filter(History.user_id == user_id)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return history, total

    def get_history_by_scenario_id(self, scenario_id: int, page: int = 1, size: int = 10):
        total = self.db.query(History).filter(History.scenario_id == scenario_id).count()
        history = (
            self.db.query(History)
            .options(joinedload(History.scenario))
            .filter(History.scenario_id == scenario_id)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return history, total
    
    def delete_history(self, history_id: int) -> bool:
        history = self.get_history_by_id(history_id)
        if not history:
            return False
        self.db.delete(history)
        self.db.commit()
        return True