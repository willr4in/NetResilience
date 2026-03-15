import networkx as nx
import random
from typing import Dict, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def calculate_betweenness(G: nx.Graph, sample_size: Optional[int] = None, normalized: bool = True, weight: Optional[str] = "weight") -> Dict[str, float]:
    try:
        n_nodes = len(G.nodes())

        k = sample_size
        if k is None and n_nodes > settings.MAX_NODES_FOR_FULL_CALCULATION:
            k = settings.BETWEENNESS_SAMPLE_SIZE
            
        if k is not None and k < n_nodes:
            logger.info(f"Using approximation for betweenness centrality with sample size {k} out of {n_nodes} nodes.")
            nodes_sample = random.sample(list(G.nodes()), k)
            betweenness = nx.betweenness_centrality_subset(
                G, 
                sources=nodes_sample,
                targets=list(G.nodes()),
                normalized=normalized, 
                weight=weight
            )
        else:
            logger.info(f"Calculating exact betweenness centrality for {n_nodes} nodes.")
            betweenness = nx.betweenness_centrality(G, normalized=normalized, weight=weight)

        return dict(betweenness)
    
    except Exception as e:
        logger.error(f"Error calculating betweenness centrality: {e}")
        raise

def calculate_closeness(G: nx.Graph, weight: Optional[str] = "weight") -> Dict[str, float]:
    try:
        logger.info(f"Calculating closeness centrality for {len(G.nodes())} nodes.")
        closeness = nx.closeness_centrality(G, distance=weight)
        return dict(closeness)
    
    except Exception as e:
        logger.error(f"Error calculating closeness centrality: {e}")
        raise

def calculate_degree(G: nx.Graph, normalized: bool = True) -> Dict[str, float]:
    try:
        logger.info(f"Calculating degree centrality for {len(G.nodes())} nodes.")
        if normalized:
            degree = nx.degree_centrality(G)
        else:
            degree = dict(G.degree())

        return dict(degree)
    
    except Exception as e:
        logger.error(f"Error calculating degree centrality: {e}")
        raise

def calculate_all(G: nx.Graph, sample_size: Optional[int] = None, normalized: bool = True, weight: Optional[str] = 'weight') -> Dict[str, Dict[str, float]]:
    n_nodes = len(G.nodes())
    
    if n_nodes == 0:
        logger.warning("Graph is empty. Returning empty centrality measures.")
        return {"betweenness": {}, "closeness": {}, "degree": {}}
    
    logger.info(f"Calculating all centrality measures for graph with {n_nodes} nodes.")
    
    if sample_size is None and n_nodes > settings.MAX_NODES_FOR_FULL_CALCULATION:
        sample_size = settings.BETWEENNESS_SAMPLE_SIZE
        logger.info(f"Graph has {n_nodes} nodes, which exceeds the threshold of {settings.MAX_NODES_FOR_FULL_CALCULATION}. Using sample size of {sample_size} for betweenness centrality.")

    result = {
        "betweenness": calculate_betweenness(G, sample_size=sample_size, normalized=normalized, weight=weight),
        "closeness": calculate_closeness(G, weight=weight),
        "degree": calculate_degree(G, normalized=normalized)
    }

    for metric_name, values in result.items():
        if values:
            logger.debug(
                f"{metric_name}: min={min(values.values()):.4f}, max={max(values.values()):.4f}, mean={sum(values.values())/len(values):.4f}"
            )

    return result