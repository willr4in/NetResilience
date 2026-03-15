import json
import time
import networkx as nx
from pathlib import Path
from typing import Dict, Optional
import logging

from ..config import settings
from ..schemas.graph import GraphSchema, GraphChanges, GraphAnalysisResponse
from ..algorithms.centrality import calculate_all
from ..algorithms.resilience import calculate_resilience

logger = logging.getLogger(__name__)


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
            weight = float(edge[2]) if len(edge) > 2 else 1.0
            G_modified.add_edge(edge[0], edge[1], weight=weight)
            logger.debug(f"Added edge: {edge[0]} -> {edge[1]} (weight={weight})")

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

    logger.info(
        f"Analysis complete: critical_nodes={len(critical_nodes)}, "
        f"resilience_score={resilience_metrics.get('resilience_score')}"
    )

    return {
        "metrics": {
            "betweenness": centrality_metrics.get("betweenness", {}),
            "closeness": centrality_metrics.get("closeness", {}),
            "degree": centrality_metrics.get("degree", {}),
            "critical_nodes": critical_nodes
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