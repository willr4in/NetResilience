import { Fragment, memo, useEffect, useMemo, useState } from 'react'
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
  const focusTarget = useGraphStore((s) => s.focusTarget)
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const cascadeRemovedIds = useMemo(
    () => new Set((cascadeResult?.steps ?? []).map((s) => s.removed_node_id)),
    [cascadeResult]
  )
  const effectiveRemoved = useMemo(
    () => Array.from(new Set([...removedNodes, ...cascadeRemovedIds])),
    [removedNodes, cascadeRemovedIds]
  )
  const [highlightedId, setHighlightedId] = useState<string | null>(null)

  useEffect(() => {
    if (!focusTarget) return
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setHighlightedId(focusTarget.id)
    const t = setTimeout(() => setHighlightedId(null), 2500)
    return () => clearTimeout(t)
  }, [focusTarget])

  const criticalNodes = analysisResult?.metrics.critical_nodes ?? []
  const betweenness = analysisResult?.metrics.betweenness ?? {}
  const isolatedNodes = analysisResult?.metrics.isolated_nodes ?? []

  const handleNodeClick = (nodeId: string, isAdded: boolean) => {
    if (mapMode === 'delete') {
      // Добавленные узлы удаляются через undo, не через toggle
      if (!isAdded) toggleNode(nodeId)
    } else if (mapMode === 'add-edge') {
      // Нельзя тянуть ребро к/от удалённого узла
      const isRemoved = removedNodes.includes(nodeId) || cascadeRemovedIds.has(nodeId)
      if (isRemoved) return
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
        const isRemovedByUser = removedNodes.includes(node.id)
        const isCascadeRemoved = cascadeRemovedIds.has(node.id)
        const isRemoved = isRemovedByUser || isCascadeRemoved
        const isSelected = selectedNodeId === node.id
        const isHighlighted = highlightedId === node.id
        const color = node.isAdded
          ? '#22c55e'
          : isSelected
          ? '#f59e0b'
          : nodeColor(node.id, effectiveRemoved, criticalNodes, betweenness, isolatedNodes)
        const opacity = node.isAdded ? 0.9 : nodeOpacity(node.id, effectiveRemoved)

        return (
          <Fragment key={node.id}>
            {isHighlighted && (
              <CircleMarker
                center={[node.lat, node.lon]}
                radius={16}
                pathOptions={{
                  color: '#f59e0b',
                  fillColor: '#f59e0b',
                  fillOpacity: 0.15,
                  weight: 2,
                  dashArray: '4 3',
                }}
                interactive={false}
              />
            )}
            <CircleMarker
              center={[node.lat, node.lon]}
              radius={isHighlighted ? 9 : isSelected ? 8 : isRemoved ? 5 : 6}
              pathOptions={{
                color: isHighlighted ? '#f59e0b' : isSelected ? '#f59e0b' : color,
                fillColor: color,
                fillOpacity: opacity,
                weight: isHighlighted || isSelected ? 2 : 1,
              }}
              eventHandlers={
                mapMode === 'delete' || mapMode === 'add-edge'
                  ? { click: () => handleNodeClick(node.id, node.isAdded) }
                  : {}
              }
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.9}>
                <span className="text-xs">{node.label}</span>
                {isRemovedByUser && <span className="text-red-500 ml-1">(удалён)</span>}
                {isCascadeRemoved && !isRemovedByUser && <span className="text-red-500 ml-1">(каскад)</span>}
                {isSelected && <span className="text-amber-500 ml-1">(выбран)</span>}
                {node.isAdded && <span className="text-green-500 ml-1">(новый)</span>}
              </Tooltip>
            </CircleMarker>
          </Fragment>
        )
      })}
    </>
  )
}

export default memo(NodeLayer)
