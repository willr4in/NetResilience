from fastapi import APIRouter, Depends, status
from ..dependencies import get_history_service, get_current_user
from ..services.history_service import HistoryService
from ..schemas.history import HistoryList
from ..models.user import User

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("", response_model=HistoryList, status_code=status.HTTP_200_OK)
def get_user_history(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    history_service: HistoryService = Depends(get_history_service)
):
    return history_service.get_user_history(user_id=current_user.id, page=page, size=size)

@router.get("/scenario/{scenario_id}", response_model=HistoryList, status_code=status.HTTP_200_OK)
def get_scenario_history(
    scenario_id: int,
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    history_service: HistoryService = Depends(get_history_service)
):
    return history_service.get_scenario_history(scenario_id, page=page, size=size)