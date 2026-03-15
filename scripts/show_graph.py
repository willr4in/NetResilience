import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_graph():
    path = Path("../backend/app/data/districts/tverskoy.json")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    G = nx.Graph()
    for node in data["nodes"]:
        G.add_node(node["id"], lat=node["lat"], lon=node["lon"])
    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"])
    
    pos = {node: (data["lon"], data["lat"]) for node, data in G.nodes(data=True)}
    
    plt.figure(figsize=(12, 10))
    nx.draw(G, pos,
        node_size=10,
        node_color="blue",
        edge_color="gray",
        width=0.5,
        with_labels=False
    )
    plt.title("Тверской район")
    plt.savefig("tverskoy_graph.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    visualize_graph()