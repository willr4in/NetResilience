from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    CALCULATE = "calculate"
    SAVE = "save"
    DELETE = "delete"
    VIEW = "view"
    
class HistoryBase(BaseModel):
    scenario_id: Optional[int] = Field(None, description="ID of the scenario related to the action")
    action: ActionType = Field(..., description="Type of action performed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the action")

class HistoryCreate(HistoryBase):
    calculation_time_ms: Optional[float] = Field(None, description="Time taken for calculation actions in milliseconds")

class HistoryResponse(HistoryBase):
    id: int = Field(..., description="ID of the history record")
    user_id: int = Field(..., description="ID of the user performing the action")
    created_at: datetime = Field(..., description="Timestamp of when the action was performed")
    scenario_name: Optional[str] = Field(None, description="Name of the scenario related to the action")
    calculation_time_ms: Optional[float] = Field(None, description="Time taken for calculation actions in milliseconds")

    model_config = {"from_attributes": True}

class HistoryList(BaseModel):
    items: List[HistoryResponse] = Field(default_factory=list, description="List of history records")
    total: int = Field(0, description="Total number of history records")
    page: int = Field(1, description="Current page number")
    size: int = Field(10, description="Number of history records per page")
    pages: int = Field(1, description="Total number of pages")

