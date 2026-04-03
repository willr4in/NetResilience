from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class GraphMetadata(BaseModel):
    name: str = Field(..., description="Name of the graph")
    city: str = Field(..., description="City of the graph")
    district: str = Field(..., description="District of the graph")


class NodeSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Display label for the node")
    lat: float = Field(..., ge=-90, le=90, description="Latitude of the node")
    lon: float = Field(..., ge=-180, le=180, description="Longitude of the node")


class EdgeSchema(BaseModel):
    source: str = Field(..., description="Source node identifier")
    target: str = Field(..., description="Target node identifier")
    weight: float = Field(..., gt=0, description="Weight of the edge in km")


class GraphSchema(BaseModel):
    metadata: GraphMetadata = Field(..., description="Metadata for the graph")
    nodes: List[NodeSchema] = Field(..., description="List of nodes in the graph")
    edges: List[EdgeSchema] = Field(..., description="List of edges in the graph")


class GraphChanges(BaseModel):
    district: str = Field(..., description="District name")
    removed_nodes: List[str] = Field(default_factory=list)
    removed_edges: List[List[str]] = Field(default_factory=list)
    added_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    added_edges: List[List[str]] = Field(default_factory=list)


class MetricResponse(BaseModel):
    betweenness: Dict[str, float] = Field(default_factory=dict)
    closeness: Dict[str, float] = Field(default_factory=dict)
    degree: Dict[str, float] = Field(default_factory=dict)
    critical_nodes: List[str] = Field(default_factory=list)
    isolated_nodes: List[str] = Field(default_factory=list)


class GraphAnalysisResponse(BaseModel):
    metrics: MetricResponse = Field(..., description="Calculated metrics")
    resilience: Dict[str, Any] = Field(..., description="Resilience metrics")
    calculation_time_ms: float = Field(0.0, description="Calculation time in milliseconds")


class CascadeRequest(BaseModel):
    district: str = Field(..., description="District name")
    steps: int = Field(10, ge=1, le=100, description="Number of cascade steps (1–100)")


class CascadeStep(BaseModel):
    step: int = Field(..., description="Step number")
    removed_node_id: str = Field(..., description="ID of the removed node")
    removed_node_label: str = Field(..., description="Label of the removed node")
    resilience_score: float = Field(..., description="Resilience score after removal")
    connected: bool = Field(..., description="Whether the graph is still connected")
    largest_component_ratio: float = Field(..., description="Fraction of nodes in largest component")
    betweenness_concentration: float = Field(..., description="Betweenness concentration (Gini)")


class CascadeResponse(BaseModel):
    district: str = Field(..., description="District name")
    initial_resilience_score: float = Field(..., description="Resilience score before any removal")
    steps: List[CascadeStep] = Field(..., description="Cascade simulation steps")
    total_steps: int = Field(..., description="Actual number of steps executed")
    calculation_time_ms: float = Field(0.0, description="Calculation time in milliseconds")