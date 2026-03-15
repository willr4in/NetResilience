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
        """
        Возвращает историю действий пользователя с пагинацией.
        """
        history = self.history_repository.get_history_by_user_id(user_id)
        total = len(history)
        pages = math.ceil(total / size) if total > 0 else 1

        start = (page - 1) * size
        end = start + size
        paginated = history[start:end]

        logger.info(f"Retrieved history for user_id={user_id}: total={total}")
        return HistoryList(
            items=[HistoryResponse.model_validate(h) for h in paginated],
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    def get_scenario_history(self, scenario_id: int) -> List[HistoryResponse]:
        """
        Возвращает историю действий по конкретному сценарию.
        """
        history = self.history_repository.get_history_by_scenario_id(scenario_id)
        logger.info(f"Retrieved history for scenario_id={scenario_id}: total={len(history)}")
        return [HistoryResponse.model_validate(h) for h in history]

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