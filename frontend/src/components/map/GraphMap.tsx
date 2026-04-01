import { useEffect, useMemo } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { buildNodeMap, getGraphBounds } from '../../utils/normalizeGraphData'
import { DEFAULT_CENTER, DEFAULT_ZOOM, TILE_URL, TILE_ATTRIBUTION } from '../../constants/map'
import NodeLayer from './NodeLayer'
import EdgeLayer from './EdgeLayer'
import 'leaflet/dist/leaflet.css'
import '../../lib/leaflet'

function BoundsUpdater() {
  const map = useMap()
  const nodes = useGraphStore((s) => s.nodes)

  useEffect(() => {
    const bounds = getGraphBounds(nodes)
    if (bounds) map.fitBounds(bounds, { padding: [40, 40] })
  }, [nodes, map])

  return null
}

export default function GraphMap() {
  const nodes = useGraphStore((s) => s.nodes)
  const edges = useGraphStore((s) => s.edges)

  const nodeMap = useMemo(() => buildNodeMap(nodes), [nodes])

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      className="w-full h-full"
      zoomControl={true}
    >
      <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
      <BoundsUpdater />
      <EdgeLayer edges={edges} nodeMap={nodeMap} />
      <NodeLayer nodes={nodes} />
    </MapContainer>
  )
}
