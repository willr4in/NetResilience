from .database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional
from .services.user_service import UserService
from .services.scenario_service import ScenarioService
from .services.history_service import HistoryService
from .services.auth_service import AuthService
from .models.user import User

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_scenario_service(db: Session = Depends(get_db)) -> ScenarioService:
    return ScenarioService(db)

def get_history_service(db: Session = Depends(get_db)) -> HistoryService:
    return HistoryService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_current_user(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    auth_service = AuthService(db)
    payload = auth_service.decode_token(access_token)
    user = db.query(User).filter(User.id == payload.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user