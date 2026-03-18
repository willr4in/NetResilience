from fastapi import APIRouter, Depends, status
from ..dependencies import get_scenario_service
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate, ScenarioResponse, ScenarioList
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

TEST_USER_ID = 3

@router.get("", response_model=ScenarioList, status_code=status.HTTP_200_OK)
def get_all_scenarios(scenario_service: ScenarioService = Depends(get_scenario_service)):
    return scenario_service.get_user_scenarios(user_id=TEST_USER_ID)

@router.get("/{scenario_id}", response_model=ScenarioResponse, status_code=status.HTTP_200_OK)
def get_scenario(scenario_id: int, scenario_service: ScenarioService = Depends(get_scenario_service)):
    return scenario_service.get_scenario(scenario_id, user_id=TEST_USER_ID)

@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def save_scenario(scenario_data: ScenarioCreate, scenario_service: ScenarioService = Depends(get_scenario_service)):
    return scenario_service.save_scenario(user_id=TEST_USER_ID, scenario_data=scenario_data)

@router.put("/{scenario_id}", response_model=ScenarioResponse, status_code=status.HTTP_200_OK)
def update_scenario(scenario_id: int, update_data: ScenarioUpdate, scenario_service: ScenarioService = Depends(get_scenario_service)):
    return scenario_service.update_scenario(scenario_id, user_id=TEST_USER_ID, update_data=update_data)

@router.delete("/{scenario_id}", status_code=status.HTTP_200_OK)
def delete_scenario(scenario_id: int, scenario_service: ScenarioService = Depends(get_scenario_service)):
    return scenario_service.delete_scenario(scenario_id, user_id=TEST_USER_ID)