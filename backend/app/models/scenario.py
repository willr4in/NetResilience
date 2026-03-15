from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    district = Column(String, nullable=False)

    removed_nodes = Column(JSON, default=list)
    removed_edges = Column(JSON, default=list)
    added_nodes = Column(JSON, default=list)
    added_edges = Column(JSON, default=list)

    metrics = Column(JSON, default=dict)

    hits = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="scenarios")
    history = relationship("History", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Scenario(id={self.id}, name={self.name}, user_id={self.user_id})"