from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class ActionType(str, enum.Enum):
    CALCULATE = "calculate"
    SAVE = "save"
    DELETE = "delete"
    VIEW = "view"

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)
    action = Column(Enum(ActionType), nullable=False)
    details = Column(JSON, default=dict)
    calculation_time_ms = Column(Float, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="history")
    scenario = relationship("Scenario", back_populates="history")

    def __repr__(self):
        return f"History(id={self.id}, user_id={self.user_id}, action={self.action})"