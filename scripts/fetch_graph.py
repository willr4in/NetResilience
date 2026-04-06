import osmnx as ox
import networkx as nx
import json
from pathlib import Path
from shapely.ops import unary_union

DISTRICTS = [
    "Тверской район, Москва, Россия",
    "Marina Roshcha, Moscow, Russia",
    "Савёловский район, Москва, Россия",
    "Беговой, Москва, Россия",
    "Сокол, Москва, Россия",
    "Аэропорт, Москва, Россия",
    "Хорошёвский район, Москва, Россия",
]

OUTPUT_PATH = Path("../backend/app/data/districts/compare.json")


def fetch_union_polygon():
    polygons = []
    for district in DISTRICTS:
        print(f"  Загрузка: {district}...")
        try:
            gdf = ox.geocode_to_gdf(district)
            geom = gdf.geometry.values[0]
            G_part = ox.graph_from_polygon(geom, network_type="drive", simplify=True)
            print(f"    {G_part.number_of_nodes()} узлов, {G_part.number_of_edges()} рёбер")
            polygons.append(geom)
        except Exception as e:
            print(f"    ОШИБКА: {e}")
    if not polygons:
        raise RuntimeError("Не удалось геокодировать ни один район")
    return unary_union(polygons)


def build_graph_data(G: nx.Graph) -> dict:
    nodes = [
        {
            "id": str(node_id),
            "label": str(node_id),
            "lat": data["y"],
            "lon": data["x"],
            "routes": [],
        }
        for node_id, data in G.nodes(data=True)
    ]

    seen: set[tuple] = set()
    edges = []
    for u, v, data in G.edges(data=True):
        key = tuple(sorted([str(u), str(v)]))
        if key not in seen:
            seen.add(key)
            edges.append({
                "source": str(u),
                "target": str(v),
                "weight": round(data.get("length", 1.0) / 1000, 4),
            })

    return {
        "metadata": {
            "name": "Тверской, Марьина Роща, Савёловский, Беговой, Сокол, Аэропорт, Хорошёвский",
            "city": "Москва",
            "district": "compare",
        },
        "nodes": nodes,
        "edges": edges,
    }


def main():
    print("Загрузка графа районов Москвы...")
    polygon = fetch_union_polygon()
    print("Загрузка дорожного графа из объединённого полигона...")
    G = ox.graph_from_polygon(polygon, network_type="drive", simplify=True)
    print(f"Загружено: {G.number_of_nodes()} узлов, {G.number_of_edges()} рёбер")

    graph_data = build_graph_data(G)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print(f"Сохранено: {OUTPUT_PATH}")
    print(f"Узлов: {len(graph_data['nodes'])}, Рёбер: {len(graph_data['edges'])}")


if __name__ == "__main__":
    main()
