from sqlalchemy.orm import Session
from ..repositories.scenario_repository import ScenarioRepository
from ..repositories.history_repository import HistoryRepository
from ..schemas.scenario import ScenarioCreate, ScenarioResponse, ScenarioUpdate, ScenarioList
from ..schemas.graph import GraphChanges
from ..schemas.history import HistoryCreate, ActionType
from ..services.graph_service import analyze, district_exists
from fastapi import HTTPException, status
import logging
import math

logger = logging.getLogger(__name__)


class ScenarioService:
    def __init__(self, db: Session):
        self.scenario_repository = ScenarioRepository(db)
        self.history_repository = HistoryRepository(db)

    def save_scenario(self, user_id: int, scenario_data: ScenarioCreate) -> ScenarioResponse:
        if not district_exists(scenario_data.district):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Граф для района '{scenario_data.district}' не найден"
            )

        changes = GraphChanges(
            district=scenario_data.district,
            removed_nodes=scenario_data.removed_nodes,
            removed_edges=scenario_data.removed_edges,
            added_nodes=scenario_data.added_nodes,
            added_edges=scenario_data.added_edges
        )

        try:
            analysis = analyze(changes)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Граф для района '{scenario_data.district}' не найден"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

        scenario = self.scenario_repository.create_scenario(
            user_id=user_id,
            scenario_data=scenario_data,
            metrics=analysis.metrics.model_dump()
        )

        self.history_repository.create_history(
            user_id=user_id,
            history_data=HistoryCreate(
                scenario_id=scenario.id,
                action=ActionType.SAVE,
                details={
                    "district": scenario_data.district,
                    "scenario_name": scenario_data.name,
                    "removed_nodes_count": len(scenario_data.removed_nodes),
                    "removed_edges_count": len(scenario_data.removed_edges),
                    "added_nodes_count": len(scenario_data.added_nodes),
                    "added_edges_count": len(scenario_data.added_edges),
                    "resilience_score": round(analysis.resilience.get("resilience_score", 0) * 100, 1),
                },
                calculation_time_ms=analysis.calculation_time_ms
            )
        )

        logger.info(f"Scenario saved: id={scenario.id}, user_id={user_id}")
        return ScenarioResponse.model_validate(scenario)

    def record_view(self, scenario_id: int, user_id: int) -> None:
        scenario = self.scenario_repository.get_scenario_by_id(scenario_id)
        if not scenario:
            return
        already_viewed = self.history_repository.has_user_viewed_scenario(user_id, scenario_id)
        if not already_viewed:
            self.scenario_repository.increment_hits(scenario_id)
            self.history_repository.create_history(
                user_id=user_id,
                history_data=HistoryCreate(
                    scenario_id=scenario_id,
                    action=ActionType.VIEW,
                    details={"scenario_name": scenario.name}
                )
            )
        logger.info(f"Scenario view recorded: id={scenario_id}, user_id={user_id}, new={not already_viewed}")

    def get_scenario(self, scenario_id: int, user_id: int) -> ScenarioResponse:
        scenario = self.scenario_repository.get_scenario_by_id(scenario_id)
        if not scenario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сценарий не найден")

        if scenario.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому сценарию")

        logger.info(f"Scenario viewed: id={scenario_id}, user_id={user_id}")
        return ScenarioResponse.model_validate(scenario)

    def get_user_scenarios(self, user_id: int, page: int = 1, size: int = 10) -> ScenarioList:
        scenarios, total = self.scenario_repository.get_scenarios_by_user_id(user_id, page, size)
        pages = math.ceil(total / size) if total > 0 else 1

        logger.info(f"Retrieved scenarios for user_id={user_id}: total={total}")
        return ScenarioList(
            items=[ScenarioResponse.model_validate(s) for s in scenarios],
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    def get_all_scenarios(self, page: int = 1, size: int = 10) -> ScenarioList:
        scenarios, total = self.scenario_repository.get_all_scenarios(page, size)
        pages = math.ceil(total / size) if total > 0 else 1

        items = []
        for s in scenarios:
            data = ScenarioResponse.model_validate(s)
            if s.user:
                data.author_name = f"{s.user.name} {s.user.surname}"
            items.append(data)

        return ScenarioList(items=items, total=total, page=page, size=size, pages=pages)

    def update_scenario(self, scenario_id: int, user_id: int, update_data: ScenarioUpdate) -> ScenarioResponse:
        scenario = self.scenario_repository.get_scenario_by_id(scenario_id)
        if not scenario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сценарий не найден")

        if scenario.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому сценарию")

        updated = self.scenario_repository.update_scenario(scenario_id, update_data)
        logger.info(f"Scenario updated: id={scenario_id}, user_id={user_id}")
        return ScenarioResponse.model_validate(updated)

    def delete_scenario(self, scenario_id: int, user_id: int) -> dict:
        scenario = self.scenario_repository.get_scenario_by_id(scenario_id)
        if not scenario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сценарий не найден")

        if scenario.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому сценарию")

        self.scenario_repository.delete_scenario(scenario_id)

        self.history_repository.create_history(
            user_id=user_id,
            history_data=HistoryCreate(
                scenario_id=None,
                action=ActionType.DELETE,
                details={"deleted_scenario_name": scenario.name}
            )
        )

        logger.info(f"Scenario deleted: id={scenario_id}, user_id={user_id}")
        return {"message": f"Scenario '{scenario.name}' deleted successfully"}