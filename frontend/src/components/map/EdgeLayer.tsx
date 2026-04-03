import { memo, Fragment } from 'react'
import { Polyline } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { getEdgePositions } from '../../utils/normalizeGraphData'
import type { EdgeSchema } from '../../types/graph'
import type { NodeMap } from '../../utils/normalizeGraphData'

interface Props {
  edges: EdgeSchema[]
  nodeMap: NodeMap
  addedEdges: string[][]
  extendedNodeMap: NodeMap
}

function EdgeLayer({ edges, nodeMap, addedEdges, extendedNodeMap }: Props) {
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const toggleEdge = useGraphStore((s) => s.toggleEdge)
  const mapMode = useGraphStore((s) => s.mapMode)

  return (
    <>
      {edges.map((edge) => {
        const positions = getEdgePositions(edge.source, edge.target, nodeMap)
        if (!positions) return null

        const isRemoved = removedEdges.some(
          ([s, t]) => s === edge.source && t === edge.target
        )

        return (
          <Fragment key={`${edge.source}-${edge.target}`}>
            <Polyline
              positions={positions}
              pathOptions={{
                color: isRemoved ? '#ef4444' : '#64748b',
                weight: isRemoved ? 2 : 1.5,
                opacity: isRemoved ? 0.5 : 0.6,
                dashArray: isRemoved ? '6 4' : undefined,
              }}
            />
            <Polyline
              positions={positions}
              pathOptions={{ color: 'transparent', weight: 12, opacity: 0 }}
              eventHandlers={mapMode === 'delete' ? { click: () => toggleEdge(edge.source, edge.target) } : {}}
            />
          </Fragment>
        )
      })}

      {addedEdges.map(([source, target]) => {
        const positions = getEdgePositions(source, target, extendedNodeMap)
        if (!positions) return null

        return (
          <Polyline
            key={`added-${source}-${target}`}
            positions={positions}
            pathOptions={{ color: '#22c55e', weight: 2, opacity: 0.8, dashArray: '6 4' }}
          />
        )
      })}
    </>
  )
}

export default memo(EdgeLayer)
