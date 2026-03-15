from fastapi import APIRouter, status, HTTPException
from ..services.graph_service import load_graph, analyze
from ..schemas.graph import GraphSchema, GraphChanges, GraphAnalysisResponse

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("/{district}", response_model=GraphSchema, status_code=status.HTTP_200_OK)
def get_graph(district: str):
    try:
        graph_schema, _ = load_graph(district)
        return graph_schema
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Graph '{district}' not found")

@router.post("/calculate", response_model=GraphAnalysisResponse, status_code=status.HTTP_200_OK)
def calculate(changes: GraphChanges):
    try:
        return analyze(changes)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Graph '{changes.district}' not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))