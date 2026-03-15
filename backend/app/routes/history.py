from fastapi import APIRouter, Depends, status
from typing import List
from ..dependencies import get_history_service
from ..services.history_service import HistoryService
from ..schemas.history import HistoryResponse, HistoryList

router = APIRouter(prefix="/api/history", tags=["history"])

TEST_USER_ID = 1

@router.get("", response_model=HistoryList, status_code=status.HTTP_200_OK)
def get_user_history(history_service: HistoryService = Depends(get_history_service)):
    return history_service.get_user_history(user_id=TEST_USER_ID)

@router.get("/scenario/{scenario_id}", response_model=List[HistoryResponse], status_code=status.HTTP_200_OK)
def get_scenario_history(scenario_id: int, history_service: HistoryService = Depends(get_history_service)):
    return history_service.get_scenario_history(scenario_id)