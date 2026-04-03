import json
import time
import math
import networkx as nx
from pathlib import Path
from typing import Dict, Optional
import logging

from ..config import settings
from ..schemas.graph import GraphSchema, GraphChanges, GraphAnalysisResponse, CascadeRequest, CascadeStep, CascadeResponse
from ..algorithms.centrality import calculate_all
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
            if len(edge) > 2:
                weight = float(edge[2])
            elif G_modified.has_node(source) and G_modified.has_node(target):
                s = G_modified.nodes[source]
                t = G_modified.nodes[target]
                weight = haversine(s["lat"], s["lon"], t["lat"], t["lon"])
            else:
                weight = 1.0
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

    Betweenness рассчитывается один раз на исходном графе — порядок удаления
    фиксируется заранее. На каждом шаге пересчитываются только дешёвые метрики
    (связность, размер компоненты, концентрация), без average_shortest_path.
    """
    start_time = time.time()

    _, G = load_graph(request.district)

    initial_centrality = calculate_all(G)
    betweenness_original = initial_centrality.get("betweenness", {})

    initial_resilience = calculate_resilience(G, initial_centrality)
    initial_score = initial_resilience["resilience_score"]

    ranked_nodes = sorted(betweenness_original, key=betweenness_original.get, reverse=True)

    G_current = G.copy()
    current_betweenness = dict(betweenness_original)
    cascade_steps = []

    actual_steps = min(request.steps, len(ranked_nodes))

    for i in range(actual_steps):
        node_id = ranked_nodes[i]

        if not G_current.has_node(node_id):
            logger.warning(f"Cascade step {i + 1}: node {node_id} already removed, skipping")
            continue

        node_label = G_current.nodes[node_id].get("label", node_id)
        G_current.remove_node(node_id)
        current_betweenness.pop(node_id, None)

        connected = is_connected(G_current) if len(G_current.nodes()) > 0 else False
        comp_ratio = largest_component_ratio(G_current)
        concentration = betweenness_concentration(current_betweenness)

        # Формула идентична calculate_resilience, но без average_shortest_path
        # (дорогая операция O(V^2), нецелесообразна при N итерациях каскада)
        resilience_score = round(
            0.4 * (1.0 if connected else 0.0) +
            0.3 * comp_ratio +
            0.3 * (1.0 - concentration),
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