import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, TileLayer, ZoomControl, useMap, useMapEvents } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { buildNodeMap, getGraphBounds } from '../../utils/normalizeGraphData'
import { DEFAULT_CENTER, DEFAULT_ZOOM, TILE_URL, MAP_BOUNDS, MAP_MIN_ZOOM } from '../../constants/map'
import NodeLayer from './NodeLayer'
import EdgeLayer from './EdgeLayer'
import 'leaflet/dist/leaflet.css'
import '../../styles/leaflet-overrides.css'
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

function MapClickHandler() {
  const mapMode = useGraphStore((s) => s.mapMode)
  const addNode = useGraphStore((s) => s.addNode)
  const counter = useRef(1)

  useMapEvents({
    click(e) {
      if (mapMode !== 'add-node') return
      const id = `new_${Date.now()}`
      addNode({
        id,
        lat: e.latlng.lat,
        lon: e.latlng.lng,
        label: `Узел ${counter.current++}`,
        node_type: 'intersection',
      })
    },
  })

  return null
}

export default function GraphMap() {
  const nodes = useGraphStore((s) => s.nodes)
  const edges = useGraphStore((s) => s.edges)
  const addedNodes = useGraphStore((s) => s.addedNodes)
  const addedEdges = useGraphStore((s) => s.addedEdges)

  const nodeMap = useMemo(() => buildNodeMap(nodes), [nodes])
  const extendedNodeMap = useMemo(() => {
    const map = buildNodeMap(nodes)
    addedNodes.forEach((n) => { map[n.id] = n })
    return map
  }, [nodes, addedNodes])

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      minZoom={MAP_MIN_ZOOM}
      maxBounds={MAP_BOUNDS}
      maxBoundsViscosity={1.0}
      className="w-full h-full"
      zoomControl={false}
    >
      <ZoomControl zoomInTitle="Приблизить" zoomOutTitle="Отдалить" />
      <TileLayer url={TILE_URL} attribution="" />
      <BoundsUpdater />
      <MapClickHandler />
      <EdgeLayer edges={edges} nodeMap={nodeMap} addedEdges={addedEdges} extendedNodeMap={extendedNodeMap} />
      <NodeLayer nodes={nodes} addedNodes={addedNodes} />
    </MapContainer>
  )
}
