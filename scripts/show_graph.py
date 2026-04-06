import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("../backend/app/data/districts/compare.json")


def load_graph(path: Path) -> tuple[nx.Graph, dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.Graph()
    for node in data["nodes"]:
        G.add_node(node["id"], lat=node["lat"], lon=node["lon"])
    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

    return G, data


def main():
    G, data = load_graph(DATA_PATH)

    name = data["metadata"].get("name", "Граф")
    print(f"Загружено: {G.number_of_nodes()} узлов, {G.number_of_edges()} рёбер")
    print(f"Связных компонент: {nx.number_connected_components(G)}")

    pos = {node: (attrs["lon"], attrs["lat"]) for node, attrs in G.nodes(data=True)}

    plt.figure(figsize=(14, 11))
    nx.draw(
        G, pos,
        node_size=8,
        node_color="steelblue",
        edge_color="#aaaaaa",
        width=0.4,
        with_labels=False,
    )
    plt.title(name, fontsize=13)
    plt.show()


if __name__ == "__main__":
    main()
