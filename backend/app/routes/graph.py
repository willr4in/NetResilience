import time
from fastapi import APIRouter, status, HTTPException
from ..services.graph_service import load_graph, analyze, simulate_cascade
from ..schemas.graph import GraphSchema, GraphChanges, GraphAnalysisResponse, CascadeRequest, CascadeResponse
from ..services import cache_service
from ..config import settings

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/{district}", response_model=GraphSchema, status_code=status.HTTP_200_OK)
def get_graph(district: str):
    key = cache_service.make_graph_key(district)
    cached = cache_service.get(key)
    if cached is not None:
        return cached
    try:
        graph_schema, _ = load_graph(district)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Граф '{district}' не найден")
    result = graph_schema.model_dump()
    cache_service.set(key, result, settings.REDIS_TTL_GRAPH)
    return result


@router.post("/calculate", response_model=GraphAnalysisResponse, status_code=status.HTTP_200_OK)
def calculate(changes: GraphChanges):
    key = cache_service.make_analysis_key(changes.model_dump())
    t0 = time.monotonic()
    cached = cache_service.get(key)
    if cached is not None:
        cached["calculation_time_ms"] = round((time.monotonic() - t0) * 1000, 2)
        return cached
    try:
        result = analyze(changes)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Граф '{changes.district}' не найден")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    dumped = result.model_dump()
    cache_service.set(key, dumped, settings.REDIS_TTL_ANALYSIS)
    return dumped


@router.post("/simulate-cascade", response_model=CascadeResponse, status_code=status.HTTP_200_OK)
def cascade(request: CascadeRequest):
    key = cache_service.make_cascade_key(request.model_dump())
    t0 = time.monotonic()
    cached = cache_service.get(key)
    if cached is not None:
        cached["calculation_time_ms"] = round((time.monotonic() - t0) * 1000, 2)
        return cached
    try:
        result = simulate_cascade(request)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Граф '{request.district}' не найден")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    dumped = result.model_dump()
    cache_service.set(key, dumped, settings.REDIS_TTL_CASCADE)
    return dumped
