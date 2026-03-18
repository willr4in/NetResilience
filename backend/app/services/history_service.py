from sqlalchemy.orm import Session
from typing import List
from ..repositories.history_repository import HistoryRepository
from ..schemas.history import HistoryResponse, HistoryList
from fastapi import HTTPException, status
import logging
import math

logger = logging.getLogger(__name__)


class HistoryService:
    def __init__(self, db: Session):
        self.history_repository = HistoryRepository(db)

    def get_user_history(self, user_id: int, page: int = 1, size: int = 10) -> HistoryList:
        history, total = self.history_repository.get_history_by_user_id(user_id, page, size)
        pages = math.ceil(total / size) if total > 0 else 1

        items = []
        for h in history:
            h_dict = {
                "id": h.id,
                "user_id": h.user_id,
                "scenario_id": h.scenario_id,
                "action": h.action,
                "details": h.details,
                "calculation_time_ms": h.calculation_time_ms,
                "created_at": h.created_at,
                "scenario_name": h.scenario.name if h.scenario else None
            }
            items.append(HistoryResponse(**h_dict))

        return HistoryList(items=items, total=total, page=page, size=size, pages=pages)

    def get_scenario_history(self, scenario_id: int, page: int = 1, size: int = 10) -> HistoryList:
        history, total = self.history_repository.get_history_by_scenario_id(scenario_id, page, size)
        pages = math.ceil(total / size) if total > 0 else 1

        items = []
        for h in history:
            h_dict = {
                "id": h.id,
                "user_id": h.user_id,
                "scenario_id": h.scenario_id,
                "action": h.action,
                "details": h.details,
                "calculation_time_ms": h.calculation_time_ms,
                "created_at": h.created_at,
                "scenario_name": h.scenario.name if h.scenario else None
            }
            items.append(HistoryResponse(**h_dict))

        return HistoryList(items=items, total=total, page=page, size=size, pages=pages)

    def delete_history_record(self, history_id: int) -> dict:
        """
        Удаляет запись из истории.
        """
        deleted = self.history_repository.delete_history(history_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History record not found"
            )
        logger.info(f"History record deleted: id={history_id}")
        return {"message": f"History record {history_id} deleted successfully"}