from fastapi import APIRouter, Depends, status
from ..dependencies import get_scenario_service, get_current_user
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate, ScenarioResponse, ScenarioList
from ..services.scenario_service import ScenarioService
from ..models.user import User

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

@router.get("/public", response_model=ScenarioList, status_code=status.HTTP_200_OK)
def get_public_scenarios(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.get_all_scenarios(page=page, size=size)

@router.get("", response_model=ScenarioList, status_code=status.HTTP_200_OK)
def get_all_scenarios(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.get_user_scenarios(user_id=current_user.id, page=page, size=size)

@router.get("/{scenario_id}", response_model=ScenarioResponse, status_code=status.HTTP_200_OK)
def get_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.get_scenario(scenario_id, user_id=current_user.id)

@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def save_scenario(
    scenario_data: ScenarioCreate,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.save_scenario(user_id=current_user.id, scenario_data=scenario_data)

@router.put("/{scenario_id}", response_model=ScenarioResponse, status_code=status.HTTP_200_OK)
def update_scenario(
    scenario_id: int,
    update_data: ScenarioUpdate,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.update_scenario(scenario_id, user_id=current_user.id, update_data=update_data)

@router.post("/{scenario_id}/view", status_code=status.HTTP_200_OK)
def view_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    scenario_service.record_view(scenario_id, user_id=current_user.id)
    return {"ok": True}

@router.delete("/{scenario_id}", status_code=status.HTTP_200_OK)
def delete_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    return scenario_service.delete_scenario(scenario_id, user_id=current_user.id)