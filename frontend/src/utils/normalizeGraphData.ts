import type { NodeSchema, GraphSchema } from '../types/graph'

export type NodeMap = Record<string, NodeSchema>

export function buildNodeMap(nodes: NodeSchema[]): NodeMap {
  return Object.fromEntries(nodes.map((n) => [n.id, n]))
}

export function getEdgePositions(
  source: string,
  target: string,
  nodeMap: NodeMap
): [[number, number], [number, number]] | null {
  const s = nodeMap[source]
  const t = nodeMap[target]
  if (!s || !t) return null
  return [
    [s.lat, s.lon],
    [t.lat, t.lon],
  ]
}

export function getGraphBounds(nodes: NodeSchema[]): [[number, number], [number, number]] | null {
  if (nodes.length === 0) return null
  const lats = nodes.map((n) => n.lat)
  const lons = nodes.map((n) => n.lon)
  return [
    [Math.min(...lats), Math.min(...lons)],
    [Math.max(...lats), Math.max(...lons)],
  ]
}

export function extractChanges(graph: GraphSchema, removedNodes: string[], removedEdges: string[][]) {
  return {
    district: graph.metadata.district,
    removed_nodes: removedNodes,
    removed_edges: removedEdges,
    added_nodes: [],
    added_edges: [],
  }
}
