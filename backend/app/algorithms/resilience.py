import networkx as nx
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


def is_connected(G: nx.Graph) -> bool:
    """Проверяет связность графа."""
    return nx.is_connected(G)


def largest_component_ratio(G: nx.Graph) -> float:
    """
    Доля узлов в наибольшей связной компоненте.
    1.0 = граф полностью связен
    0.5 = половина узлов отрезана
    """
    if len(G.nodes()) == 0:
        return 0.0
    largest = max(nx.connected_components(G), key=len)
    return len(largest) / len(G.nodes())


def average_shortest_path(G: nx.Graph, weight: str = "weight") -> Optional[float]:
    """
    Средняя длина кратчайшего пути.
    Если граф несвязен — считаем только по наибольшей компоненте.
    """
    if len(G.nodes()) == 0:
        return None
    
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)  # ← сначала определили
        logger.warning(
            f"Graph is not connected. Calculating on largest component "
            f"({len(largest)}/{len(G.nodes())} nodes)."
        )
        G = G.subgraph(largest).copy()
    
    try:
        return nx.average_shortest_path_length(G, weight=weight)
    except Exception as e:
        logger.error(f"Error calculating average shortest path: {e}")
        return None


def betweenness_concentration(centrality_metrics: Dict[str, float]) -> float:
    """
    Концентрация betweenness — насколько нагрузка сосредоточена в нескольких узлах.
    0.0 = равномерно распределена (устойчиво)
    1.0 = вся нагрузка на одном узле (хрупко)
    Используем коэффициент Джини.
    """
    values = sorted(centrality_metrics.values())
    n = len(values)
    if n == 0 or sum(values) == 0:
        return 0.0
    
    cumulative = sum((i + 1) * v for i, v in enumerate(values))
    total = sum(values)
    
    if total == 0:
        return 0.0
    
    gini = (2 * cumulative) / (n * total) - (n + 1) / n
    return round(gini, 4)


def top_nodes_change(
    metrics_before: Dict[str, float],
    metrics_after: Dict[str, float],
    n: int = 5
) -> Dict:
    """
    Сравнивает топ-N важных узлов до и после изменения графа.
    Показывает какие узлы появились/исчезли из топа.
    """
    top_before = set(sorted(metrics_before, key=metrics_before.get, reverse=True)[:n])
    top_after = set(sorted(metrics_after, key=metrics_after.get, reverse=True)[:n])

    return {
        "top_before": list(top_before),
        "top_after": list(top_after),
        "new_critical": list(top_after - top_before),   # новые критические узлы
        "no_longer_critical": list(top_before - top_after)  # перестали быть критическими
    }


def calculate_resilience(
    G: nx.Graph,
    centrality_metrics: Dict[str, Dict[str, float]],
    G_original: Optional[nx.Graph] = None,
    metrics_original: Optional[Dict[str, Dict[str, float]]] = None,
    weight: str = "weight"
) -> Dict:
    """
    Главная функция — считает устойчивость сети.
    
    Если переданы G_original и metrics_original — возвращает сравнение до/после.
    Если нет — просто анализирует текущее состояние.
    """
    n_nodes = len(G.nodes())
    logger.info(f"Calculating resilience for graph with {n_nodes} nodes.")

    connected = is_connected(G)
    component_ratio = largest_component_ratio(G)
    avg_path = average_shortest_path(G, weight=weight)
    concentration = betweenness_concentration(centrality_metrics.get("betweenness", {}))

    # Итоговый score от 0 до 1
    # connected: 0.4 веса, component_ratio: 0.3, concentration (инверсия): 0.3
    resilience_score = round(
        0.4 * (1.0 if connected else 0.0) +
        0.3 * component_ratio +
        0.3 * (1.0 - concentration),
        4
    )

    result = {
        "connected": connected,
        "largest_component_ratio": round(component_ratio, 4),
        "average_shortest_path": round(avg_path, 4) if avg_path else None,
        "betweenness_concentration": concentration,
        "resilience_score": resilience_score,
        "comparison": None
    }

    # Если передали оригинал — добавляем сравнение
    if G_original is not None and metrics_original is not None:
        original_score = calculate_resilience(G_original, metrics_original)["resilience_score"]
        avg_path_original = average_shortest_path(G_original, weight=weight)

        result["comparison"] = {
            "resilience_score_before": original_score,
            "resilience_score_after": resilience_score,
            "resilience_delta": round(resilience_score - original_score, 4),
            "avg_path_before": round(avg_path_original, 4) if avg_path_original else None,
            "avg_path_after": round(avg_path, 4) if avg_path else None,
            "avg_path_delta": round(
                (avg_path - avg_path_original), 4
            ) if avg_path and avg_path_original else None,
            "top_nodes_change": top_nodes_change(
                metrics_original.get("betweenness", {}),
                centrality_metrics.get("betweenness", {})
            )
        }
        
        logger.info(
            f"Resilience: {original_score} → {resilience_score} "
            f"(delta: {result['comparison']['resilience_delta']})"
        )

    return result