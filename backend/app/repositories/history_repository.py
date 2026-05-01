from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from ..models.history import History
from ..schemas.history import HistoryCreate, ActionType

class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_history(self, user_id: int, history_data: HistoryCreate) -> History:
        history = History(
            user_id=user_id,
            scenario_id=history_data.scenario_id,
            action=history_data.action,
            details=history_data.details,
            calculation_time_ms=history_data.calculation_time_ms
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def get_history_by_id(self, history_id: int) -> Optional[History]:
        return self.db.query(History).options(
            joinedload(History.scenario)
        ).filter(History.id == history_id).first()
    
    def get_history_by_user_id(self, user_id: int, page: int = 1, size: int = 10,
                                action: str = "", search: str = ""):
        q = (
            self.db.query(History)
            .options(joinedload(History.scenario))
            .filter(History.user_id == user_id)
        )
        if action:
            q = q.filter(History.action == action)
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    History.details.op('->>')('scenario_name').ilike(term),
                    History.details.op('->>')('deleted_scenario_name').ilike(term),
                )
            )
        total = q.count()
        history = q.order_by(History.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return history, total

    def get_history_by_scenario_id(self, scenario_id: int, page: int = 1, size: int = 10):
        total = self.db.query(History).filter(History.scenario_id == scenario_id).count()
        history = (
            self.db.query(History)
            .options(joinedload(History.scenario))
            .filter(History.scenario_id == scenario_id)
            .order_by(History.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return history, total
    
    def has_user_viewed_scenario(self, user_id: int, scenario_id: int) -> bool:
        return self.db.query(History).filter(
            History.user_id == user_id,
            History.scenario_id == scenario_id,
            History.action == ActionType.VIEW
        ).first() is not None

    def delete_history(self, history_id: int) -> bool:
        history = self.get_history_by_id(history_id)
        if not history:
            return False
        self.db.delete(history)
        self.db.commit()
        return True