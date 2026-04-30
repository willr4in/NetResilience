import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, TileLayer, ZoomControl, useMap, useMapEvents } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'
import { buildNodeMap, getGraphBounds } from '../../utils/normalizeGraphData'
import { DEFAULT_CENTER, DEFAULT_ZOOM, TILE_URL, MAP_BOUNDS, MAP_MIN_ZOOM } from '../../constants/map'
import NodeLayer from './NodeLayer'
import EdgeLayer from './EdgeLayer'
import RouteLayer from './RouteLayer'
import HeatLayer from './HeatLayer'
import MapFocuser from './MapFocuser'
import { setMapInstance } from '../../lib/mapRef'

function MapInstanceProbe() {
  const map = useMap()
  useEffect(() => {
    setMapInstance(map)
    return () => setMapInstance(null)
  }, [map])
  return null
}
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
  const setRoutePin = useGraphStore((s) => s.setRoutePin)
  const routeFrom = useGraphStore((s) => s.routeFrom)
  const routeTo = useGraphStore((s) => s.routeTo)
  const counter = useRef(1)

  useMapEvents({
    click(e) {
      if (mapMode === 'add-node') {
        const id = `new_${Date.now()}`
        addNode({
          id,
          lat: e.latlng.lat,
          lon: e.latlng.lng,
          label: `Узел ${counter.current++}`,
          node_type: 'intersection',
        })
        return
      }
      if (mapMode === 'route') {
        const pin = { lat: e.latlng.lat, lon: e.latlng.lng }
        if (!routeFrom) {
          setRoutePin('from', pin)
        } else if (!routeTo) {
          setRoutePin('to', pin)
        } else {
          setRoutePin('from', pin)
          setRoutePin('to', null)
        }
      }
    },
  })

  return null
}

export default function GraphMap() {
  const nodes = useGraphStore((s) => s.nodes)
  const edges = useGraphStore((s) => s.edges)
  const addedNodes = useGraphStore((s) => s.addedNodes)
  const addedEdges = useGraphStore((s) => s.addedEdges)
  const viewMode = useGraphStore((s) => s.viewMode)

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
      <MapInstanceProbe />
      <MapFocuser />
      <MapClickHandler />
      <EdgeLayer edges={edges} nodeMap={nodeMap} addedEdges={addedEdges} extendedNodeMap={extendedNodeMap} />
      {viewMode === 'points' ? (
        <NodeLayer nodes={nodes} addedNodes={addedNodes} />
      ) : (
        <HeatLayer />
      )}
      <RouteLayer />
    </MapContainer>
  )
}
