from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.scenario import Scenario
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate

class ScenarioRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_scenario(self, user_id: int, scenario_data: ScenarioCreate, metrics: dict = None) -> Scenario:
        scenario = Scenario(
            user_id=user_id,
            name=scenario_data.name,
            description=scenario_data.description,
            district=scenario_data.district,
            removed_nodes=scenario_data.removed_nodes,
            removed_edges=scenario_data.removed_edges,
            added_nodes=scenario_data.added_nodes,
            added_edges=scenario_data.added_edges,
            hits=0
        )
        if metrics:
            scenario.metrics = metrics
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario
    
    def get_scenario_by_id(self, scenario_id: int) -> Optional[Scenario]:
        return self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
    
    def get_scenarios_by_user_id(self, user_id: int, page: int = 1, size: int = 10):
        total = self.db.query(Scenario).filter(Scenario.user_id == user_id).count()
        scenarios = (
            self.db.query(Scenario)
            .filter(Scenario.user_id == user_id)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return scenarios, total
        
    def get_scenarios_by_district(self, district: str) -> List[Scenario]:
        return self.db.query(Scenario).filter(Scenario.district == district).all()
    
    def update_scenario(self, scenario_id: int, scenario_data: ScenarioUpdate) -> Optional[Scenario]:
        scenario = self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None
        for key, value in scenario_data.model_dump(exclude_unset=True).items():
            setattr(scenario, key, value)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario
    
    def delete_scenario(self, scenario_id: int) -> bool:
        scenario = self.get_scenario_by_id(scenario_id)
        if not scenario:
            return False
        self.db.delete(scenario)
        self.db.commit()
        return True
    
    def increment_hits(self, scenario_id: int) -> Optional[Scenario]:
        scenario = self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None
        scenario.hits += 1
        self.db.commit()
        self.db.refresh(scenario)
        return scenario
    
    def update_metrics(self, scenario_id: int, metrics: dict) -> Optional[Scenario]:
        scenario = self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None
        scenario.metrics = metrics
        self.db.commit()
        self.db.refresh(scenario)
        return scenario