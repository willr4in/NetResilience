import osmnx as ox
import json
from pathlib import Path

def fetch_tver_district():
    
    G = ox.graph_from_place(
        "Тверской район, Москва, Россия",
        network_type="drive",
        simplify=True
    )
    
    print(f"Загружено: {len(G.nodes())} узлов, {len(G.edges())} рёбер")
    
    nodes = []
    for node_id, data in G.nodes(data=True):
        nodes.append({
            "id": str(node_id),
            "label": str(node_id),
            "lat": data["y"],
            "lon": data["x"],
            "routes": []
        })
    
    edges = []
    seen = set()
    for u, v, data in G.edges(data=True):
        key = tuple(sorted([str(u), str(v)]))
        if key not in seen:
            seen.add(key)
            edges.append({
                "source": str(u),
                "target": str(v),
                "weight": round(data.get("length", 1.0) / 1000, 4)  
            })
    
    graph_data = {
        "metadata": {
            "name": "Тверской район",
            "city": "Москва",
            "district": "tverskoy"
        },
        "nodes": nodes,
        "edges": edges
    }
    
    output_path = Path("../backend/app/data/districts/tverskoy.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    print(f"Сохранено в {output_path}")
    print(f"Узлов: {len(nodes)}, Рёбер: {len(edges)}")

if __name__ == "__main__":
    fetch_tver_district()