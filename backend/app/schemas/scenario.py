from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict
from datetime import datetime
from .graph import MetricResponse


class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Scenario name")
    description: Optional[str] = Field(None, max_length=500, description="Scenario description")
    district: str = Field(..., description="District name")

    removed_nodes: List[str] = Field(default_factory=list, description="List of removed nodes")
    removed_edges: List[List[str]] = Field(default_factory=list, description="List of removed edges")
    added_nodes: List[Dict[str, Any]] = Field(default_factory=list, description="List of added nodes")
    added_edges: List[List[str]] = Field(default_factory=list, description="List of added edges")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('Название должно содержать минимум 3 символа')
        if len(v) > 100:
            raise ValueError('Название не должно превышать 100 символов')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError('Описание не должно превышать 500 символов')
        return v


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Scenario name")
    description: Optional[str] = Field(None, max_length=500, description="Scenario description")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 3:
            raise ValueError('Название должно содержать минимум 3 символа')
        if v is not None and len(v) > 100:
            raise ValueError('Название не должно превышать 100 символов')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError('Описание не должно превышать 500 символов')
        return v


class ScenarioResponse(ScenarioBase):
    id: int = Field(..., description="ID of the scenario")
    user_id: Optional[int] = Field(None)
    author_name: Optional[str] = Field(None, description="Full name of the author")
    metrics: Optional[MetricResponse] = Field(None)
    hits: int = Field(..., description="Number of times the scenario was used")
    created_at: datetime = Field(..., description="Timestamp of when the scenario was created")
    last_used_at: Optional[datetime] = Field(None, description="Timestamp of when the scenario was last used")

    model_config = {"from_attributes": True}


class ScenarioList(BaseModel):
    items: List[ScenarioResponse] = Field(default_factory=list, description="List of scenarios")
    total: int = Field(0, description="Total number of scenarios")
    page: int = Field(1, description="Current page number")
    size: int = Field(10, description="Number of scenarios per page")
    pages: int = Field(1, description="Total number of pages")
