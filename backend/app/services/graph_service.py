import json
import time
import math
import networkx as nx
from pathlib import Path
from typing import Dict, Optional
import logging

from ..config import settings
from ..schemas.graph import (
    GraphSchema,
    GraphChanges,
    GraphAnalysisResponse,
    CascadeRequest,
    CascadeStep,
    CascadeResponse,
    RouteRequest,
    RouteResponse,
    RoutePoint,
)
from ..algorithms.centrality import calculate_all, calculate_betweenness
from ..algorithms.resilience import calculate_resilience, is_connected, largest_component_ratio, betweenness_concentration

logger = logging.getLogger(__name__)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками в км (формула Haversine). R=6371 — радиус Земли."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def district_exists(district: str) -> bool:
    path = Path(settings.DISTRICTS_DATA_PATH) / f"{district.lower()}.json"
    return path.exists()

def load_graph(district: str) -> tuple[GraphSchema, nx.Graph]:
    path = Path(settings.DISTRICTS_DATA_PATH) / f"{district.lower()}.json"

    if not path.exists():
        logger.error(f"Graph file not found: {path}")
        raise FileNotFoundError(f"Graph for district '{district}' not found")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    try:
        graph_data = GraphSchema(**raw)
    except Exception as e:
        logger.error(f"Invalid graph structure for district '{district}': {e}")
        raise ValueError(f"Invalid graph file for district '{district}': {e}")

    G = nx.Graph()
    for node in graph_data.nodes:
        G.add_node(node.id, label=node.label, lat=node.lat, lon=node.lon)
    for edge in graph_data.edges:
        G.add_edge(edge.source, edge.target, weight=edge.weight)

    logger.info(f"Graph loaded: district={district}, nodes={len(G.nodes())}, edges={len(G.edges())}")
    return graph_data, G


def apply_changes(G: nx.Graph, changes: GraphChanges) -> nx.Graph:
    """
    Применяет изменения к графу.
    Работает на копии — оригинал не трогаем.
    """
    G_modified = G.copy()

    for edge in changes.removed_edges:
        if len(edge) == 2 and G_modified.has_edge(edge[0], edge[1]):
            G_modified.remove_edge(edge[0], edge[1])
            logger.debug(f"Removed edge: {edge[0]} -> {edge[1]}")
        else:
            logger.warning(f"Edge not found: {edge}")

    for node_id in changes.removed_nodes:
        if G_modified.has_node(node_id):
            G_modified.remove_node(node_id)
            logger.debug(f"Removed node: {node_id}")
        else:
            logger.warning(f"Node not found: {node_id}")

    for node in changes.added_nodes:
        G_modified.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            lat=node.get("lat", 0.0),
            lon=node.get("lon", 0.0)
        )
        logger.debug(f"Added node: {node['id']}")

    for edge in changes.added_edges:
        if len(edge) >= 2:
            source, target = edge[0], edge[1]
            if not G_modified.has_node(source) or not G_modified.has_node(target):
                logger.warning(f"Skipping edge {source} -> {target}: endpoint not in graph")
                continue
            if len(edge) > 2:
                weight = float(edge[2])
            else:
                s = G_modified.nodes[source]
                t = G_modified.nodes[target]
                weight = haversine(s["lat"], s["lon"], t["lat"], t["lon"])
            G_modified.add_edge(source, target, weight=weight)
            logger.debug(f"Added edge: {source} -> {target} (weight={weight:.4f} km)")

    logger.info(
        f"Changes applied: "
        f"removed_nodes={len(changes.removed_nodes)}, "
        f"removed_edges={len(changes.removed_edges)}, "
        f"added_nodes={len(changes.added_nodes)}, "
        f"added_edges={len(changes.added_edges)}"
    )

    return G_modified


def run_analysis(
    G_modified: nx.Graph,
    G_original: Optional[nx.Graph] = None
) -> Dict:
    """
    Запускает полный анализ графа.
    Если передан G_original — возвращает сравнение до/после.
    """
    logger.info("Running analysis...")

    centrality_metrics = calculate_all(G_modified)

    if G_original is not None:
        original_centrality = calculate_all(G_original)
        resilience_metrics = calculate_resilience(
            G_modified,
            centrality_metrics,
            G_original=G_original,
            metrics_original=original_centrality
        )
    else:
        resilience_metrics = calculate_resilience(G_modified, centrality_metrics)

    betweenness = centrality_metrics.get("betweenness", {})
    if betweenness:
        threshold = sorted(betweenness.values(), reverse=True)[
            max(0, int(len(betweenness) * 0.2) - 1)
        ]
        critical_nodes = [
            node for node, value in betweenness.items()
            if value >= threshold
        ]
    else:
        critical_nodes = []

    if not nx.is_connected(G_modified) and len(G_modified.nodes()) > 0:
        largest = max(nx.connected_components(G_modified), key=len)
        isolated_nodes = [n for n in G_modified.nodes() if n not in largest]
    else:
        isolated_nodes = []

    logger.info(
        f"Analysis complete: critical_nodes={len(critical_nodes)}, "
        f"isolated_nodes={len(isolated_nodes)}, "
        f"resilience_score={resilience_metrics.get('resilience_score')}"
    )

    return {
        "metrics": {
            "betweenness": centrality_metrics.get("betweenness", {}),
            "closeness": centrality_metrics.get("closeness", {}),
            "degree": centrality_metrics.get("degree", {}),
            "critical_nodes": critical_nodes,
            "isolated_nodes": isolated_nodes,
        },
        "resilience": resilience_metrics
    }


def analyze(changes: GraphChanges) -> GraphAnalysisResponse:
    """
    Главная функция — загружает граф, применяет изменения, запускает анализ.
    Вызывается из роута POST /calculate
    """
    start_time = time.time()

    graph_schema, G_original = load_graph(changes.district)

    if changes.removed_nodes or changes.removed_edges or changes.added_nodes or changes.added_edges:
        G_modified = apply_changes(G_original, changes)
    else:
        G_modified = G_original
        G_original = None

    result = run_analysis(G_modified, G_original)

    calculation_time_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"Analysis completed in {calculation_time_ms}ms")

    return GraphAnalysisResponse(
        metrics=result["metrics"],
        resilience=result["resilience"],
        calculation_time_ms=calculation_time_ms
    )


def simulate_cascade(request: CascadeRequest) -> CascadeResponse:
    """
    Симулирует каскадный отказ сети: последовательно удаляет наиболее
    критичные узлы (по betweenness) и отслеживает деградацию устойчивости.

    Порядок удаления фиксируется заранее по исходному betweenness, а на каждом
    шаге betweenness пересчитывается на актуальном (уменьшившемся) графе —
    иначе концентрация (Gini) считалась бы по подмножеству исходных значений
    и давала бы недостоверный score. average_shortest_path не считаем: он
    O(V²) и в каскаде из N шагов превращается в O(N·V²).
    """
    start_time = time.time()

    _, G = load_graph(request.district)

    has_changes = (
        request.removed_nodes or request.removed_edges or
        request.added_nodes or request.added_edges
    )
    if has_changes:
        changes = GraphChanges(
            district=request.district,
            removed_nodes=request.removed_nodes,
            removed_edges=request.removed_edges,
            added_nodes=request.added_nodes,
            added_edges=request.added_edges,
        )
        G = apply_changes(G, changes)

    initial_centrality = calculate_all(G)
    betweenness_original = initial_centrality.get("betweenness", {})

    initial_resilience = calculate_resilience(G, initial_centrality)
    initial_score = initial_resilience["resilience_score"]

    ranked_nodes = sorted(betweenness_original, key=betweenness_original.get, reverse=True)

    G_current = G.copy()
    cascade_steps = []

    actual_steps = min(request.steps, len(ranked_nodes))

    for i in range(actual_steps):
        node_id = ranked_nodes[i]

        if not G_current.has_node(node_id):
            logger.warning(f"Cascade step {i + 1}: node {node_id} already removed, skipping")
            continue

        node_label = G_current.nodes[node_id].get("label", node_id)
        G_current.remove_node(node_id)

        connected = is_connected(G_current) if len(G_current.nodes()) > 0 else False
        comp_ratio = largest_component_ratio(G_current)
        # Пересчитываем betweenness на актуальном графе — без этого Gini считается
        # по подмножеству старых значений и каскад "улучшает" сеть, что ложно.
        # Идёт через тот же calculate_betweenness, что и /calculate — иначе при
        # включенной выборке (для больших графов) каскад и recalc дадут разный score.
        current_betweenness = (
            calculate_betweenness(G_current) if len(G_current.nodes()) > 0 else {}
        )
        concentration = betweenness_concentration(current_betweenness)

        # Формула идентична calculate_resilience, но без average_shortest_path
        # (дорогая операция O(V^2), нецелесообразна при N итерациях каскада)
        resilience_score = round(
            settings.RESILIENCE_WEIGHT_CONNECTIVITY * (1.0 if connected else 0.0) +
            settings.RESILIENCE_WEIGHT_LARGEST_COMPONENT * comp_ratio +
            settings.RESILIENCE_WEIGHT_BETWEENNESS_INVERSE * (1.0 - concentration),
            4
        )

        cascade_steps.append(CascadeStep(
            step=len(cascade_steps) + 1,
            removed_node_id=node_id,
            removed_node_label=node_label,
            resilience_score=resilience_score,
            connected=connected,
            largest_component_ratio=round(comp_ratio, 4),
            betweenness_concentration=round(concentration, 4)
        ))

    calculation_time_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"Cascade simulation: {len(cascade_steps)} steps, district={request.district}, {calculation_time_ms}ms")

    return CascadeResponse(
        district=request.district,
        initial_resilience_score=initial_score,
        steps=cascade_steps,
        total_steps=len(cascade_steps),
        calculation_time_ms=calculation_time_ms
    )


def _nearest_node(G: nx.Graph, lat: float, lon: float) -> tuple[str, float]:
    """Возвращает id ближайшего узла графа и расстояние до него в км (haversine)."""
    best_id: Optional[str] = None
    best_dist = float("inf")
    for node_id, data in G.nodes(data=True):
        d = haversine(lat, lon, data["lat"], data["lon"])
        if d < best_dist:
            best_dist = d
            best_id = node_id
    if best_id is None:
        raise ValueError("Граф пуст — невозможно найти ближайший узел")
    return best_id, best_dist


def find_route(request: RouteRequest) -> RouteResponse:
    """Кратчайший маршрут между двумя географическими точками с учётом изменений графа."""
    start_time = time.time()
    _, G = load_graph(request.district)

    has_changes = (
        request.removed_nodes or request.removed_edges or
        request.added_nodes or request.added_edges
    )
    if has_changes:
        changes = GraphChanges(
            district=request.district,
            removed_nodes=request.removed_nodes,
            removed_edges=request.removed_edges,
            added_nodes=request.added_nodes,
            added_edges=request.added_edges,
        )
        G = apply_changes(G, changes)

    if len(G.nodes()) == 0:
        raise ValueError("Граф пуст после применения изменений")

    src_id, snap_from_km = _nearest_node(G, request.from_lat, request.from_lon)
    dst_id, snap_to_km = _nearest_node(G, request.to_lat, request.to_lon)

    src_data = G.nodes[src_id]
    dst_data = G.nodes[dst_id]
    snap_from = RoutePoint(id=src_id, lat=src_data["lat"], lon=src_data["lon"])
    snap_to = RoutePoint(id=dst_id, lat=dst_data["lat"], lon=dst_data["lon"])
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    walk_km = snap_from_km + snap_to_km
    walk_minutes = (walk_km / settings.DEFAULT_WALKING_SPEED_KMH) * 60.0

    if src_id == dst_id:
        return RouteResponse(
            district=request.district,
            found=True,
            path=[snap_from],
            distance_km=0.0,
            drive_time_minutes=0.0,
            walk_time_minutes=round(walk_minutes, 2),
            total_time_minutes=round(walk_minutes, 2),
            snap_from=snap_from,
            snap_to=snap_to,
            snap_from_distance_km=round(snap_from_km, 4),
            snap_to_distance_km=round(snap_to_km, 4),
            calculation_time_ms=elapsed_ms,
        )

    try:
        path_ids = nx.shortest_path(G, source=src_id, target=dst_id, weight="weight")
        distance_km = nx.shortest_path_length(G, source=src_id, target=dst_id, weight="weight")
    except nx.NetworkXNoPath:
        return RouteResponse(
            district=request.district,
            found=False,
            path=[],
            distance_km=0.0,
            drive_time_minutes=0.0,
            walk_time_minutes=round(walk_minutes, 2),
            total_time_minutes=0.0,
            snap_from=snap_from,
            snap_to=snap_to,
            snap_from_distance_km=round(snap_from_km, 4),
            snap_to_distance_km=round(snap_to_km, 4),
            calculation_time_ms=round((time.time() - start_time) * 1000, 2),
        )

    points = [
        RoutePoint(id=nid, lat=G.nodes[nid]["lat"], lon=G.nodes[nid]["lon"])
        for nid in path_ids
    ]
    drive_minutes = (distance_km / settings.DEFAULT_DRIVING_SPEED_KMH) * 60.0
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"Route found: district={request.district}, hops={len(points)}, "
        f"distance_km={distance_km:.3f}, drive_min={drive_minutes:.2f}, walk_min={walk_minutes:.2f}, {elapsed_ms}ms"
    )

    return RouteResponse(
        district=request.district,
        found=True,
        path=points,
        distance_km=round(distance_km, 4),
        drive_time_minutes=round(drive_minutes, 2),
        walk_time_minutes=round(walk_minutes, 2),
        total_time_minutes=round(drive_minutes + walk_minutes, 2),
        snap_from=snap_from,
        snap_to=snap_to,
        snap_from_distance_km=round(snap_from_km, 4),
        snap_to_distance_km=round(snap_to_km, 4),
        calculation_time_ms=elapsed_ms,
    )