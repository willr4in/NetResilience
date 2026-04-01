import { memo } from 'react'
import { CircleMarker, Tooltip } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { nodeColor, nodeOpacity } from '../../utils/colorByMetric'
import type { NodeSchema } from '../../types/graph'

interface Props {
  nodes: NodeSchema[]
}

function NodeLayer({ nodes }: Props) {
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const toggleNode = useGraphStore((s) => s.toggleNode)
  const analysisResult = useGraphStore((s) => s.analysisResult)

  const criticalNodes = analysisResult?.metrics.critical_nodes ?? []
  const betweenness = analysisResult?.metrics.betweenness ?? {}

  return (
    <>
      {nodes.map((node) => {
        const isRemoved = removedNodes.includes(node.id)
        const color = nodeColor(node.id, removedNodes, criticalNodes, betweenness)
        const opacity = nodeOpacity(node.id, removedNodes)

        return (
          <CircleMarker
            key={node.id}
            center={[node.lat, node.lon]}
            radius={isRemoved ? 5 : 6}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: opacity,
              weight: 1,
            }}
            eventHandlers={{ click: () => toggleNode(node.id) }}
          >
            <Tooltip direction="top" offset={[0, -8]} opacity={0.9}>
              <span className="text-xs">{node.label}</span>
              {isRemoved && <span className="text-red-500 ml-1">(удалён)</span>}
            </Tooltip>
          </CircleMarker>
        )
      })}
    </>
  )
}

export default memo(NodeLayer)
