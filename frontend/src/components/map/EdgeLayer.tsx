import { memo } from 'react'
import { Polyline } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { getEdgePositions } from '../../utils/normalizeGraphData'
import type { EdgeSchema } from '../../types/graph'
import type { NodeMap } from '../../utils/normalizeGraphData'

interface Props {
  edges: EdgeSchema[]
  nodeMap: NodeMap
}

function EdgeLayer({ edges, nodeMap }: Props) {
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const toggleEdge = useGraphStore((s) => s.toggleEdge)

  return (
    <>
      {edges.map((edge) => {
        const positions = getEdgePositions(edge.source, edge.target, nodeMap)
        if (!positions) return null

        const isRemoved = removedEdges.some(
          ([s, t]) => s === edge.source && t === edge.target
        )

        return (
          <>
            <Polyline
              key={`${edge.source}-${edge.target}`}
              positions={positions}
              pathOptions={{
                color: isRemoved ? '#ef4444' : '#64748b',
                weight: isRemoved ? 2 : 1.5,
                opacity: isRemoved ? 0.5 : 0.6,
                dashArray: isRemoved ? '6 4' : undefined,
              }}
            />
            <Polyline
              key={`${edge.source}-${edge.target}-hit`}
              positions={positions}
              pathOptions={{
                color: 'transparent',
                weight: 12,
                opacity: 0,
              }}
              eventHandlers={{ click: () => toggleEdge(edge.source, edge.target) }}
            />
          </>
        )
      })}
    </>
  )
}

export default memo(EdgeLayer)
