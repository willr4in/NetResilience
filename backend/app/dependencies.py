from .database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from .services.user_service import UserService
from .services.scenario_service import ScenarioService
from .services.history_service import HistoryService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_scenario_service(db: Session = Depends(get_db)) -> ScenarioService:
    return ScenarioService(db)

def get_history_service(db: Session = Depends(get_db)) -> HistoryService:
    return HistoryService(db)