import { memo } from 'react'
import { CircleMarker, Tooltip } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { nodeColor, nodeOpacity } from '../../utils/colorByMetric'
import type { NodeSchema } from '../../types/graph'
import type { AddedNode } from '../../store/graphStore'

interface Props {
  nodes: NodeSchema[]
  addedNodes: AddedNode[]
}

function NodeLayer({ nodes, addedNodes }: Props) {
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const toggleNode = useGraphStore((s) => s.toggleNode)
  const analysisResult = useGraphStore((s) => s.analysisResult)
  const mapMode = useGraphStore((s) => s.mapMode)
  const selectedNodeId = useGraphStore((s) => s.selectedNodeId)
  const setSelectedNodeId = useGraphStore((s) => s.setSelectedNodeId)
  const addEdge = useGraphStore((s) => s.addEdge)

  const criticalNodes = analysisResult?.metrics.critical_nodes ?? []
  const betweenness = analysisResult?.metrics.betweenness ?? {}
  const isolatedNodes = analysisResult?.metrics.isolated_nodes ?? []

  const handleNodeClick = (nodeId: string, _isAdded: boolean) => {
    if (mapMode === 'delete') {
      toggleNode(nodeId)
    } else if (mapMode === 'add-edge') {
      if (!selectedNodeId) {
        setSelectedNodeId(nodeId)
      } else if (selectedNodeId === nodeId) {
        setSelectedNodeId(null)
      } else {
        addEdge(selectedNodeId, nodeId)
        setSelectedNodeId(null)
      }
    }
  }

  const allNodes = [
    ...nodes.map((n) => ({ ...n, isAdded: false })),
    ...addedNodes.map((n) => ({ ...n, isAdded: true })),
  ]

  return (
    <>
      {allNodes.map((node) => {
        const isRemoved = removedNodes.includes(node.id)
        const isSelected = selectedNodeId === node.id
        const color = node.isAdded
          ? '#22c55e'
          : isSelected
          ? '#f59e0b'
          : nodeColor(node.id, removedNodes, criticalNodes, betweenness, isolatedNodes)
        const opacity = node.isAdded ? 0.9 : nodeOpacity(node.id, removedNodes)

        return (
          <CircleMarker
            key={node.id}
            center={[node.lat, node.lon]}
            radius={isSelected ? 8 : isRemoved ? 5 : 6}
            pathOptions={{
              color: isSelected ? '#f59e0b' : color,
              fillColor: color,
              fillOpacity: opacity,
              weight: isSelected ? 2 : 1,
            }}
            eventHandlers={
              mapMode === 'delete' || mapMode === 'add-edge'
                ? { click: () => handleNodeClick(node.id, node.isAdded) }
                : {}
            }
          >
            <Tooltip direction="top" offset={[0, -8]} opacity={0.9}>
              <span className="text-xs">{node.label}</span>
              {isRemoved && <span className="text-red-500 ml-1">(удалён)</span>}
              {isSelected && <span className="text-amber-500 ml-1">(выбран)</span>}
              {node.isAdded && <span className="text-green-500 ml-1">(новый)</span>}
            </Tooltip>
          </CircleMarker>
        )
      })}
    </>
  )
}

export default memo(NodeLayer)
