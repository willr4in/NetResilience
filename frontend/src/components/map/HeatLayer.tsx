import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import { useGraphStore } from '../../store/graphStore'

export default function HeatLayer() {
  const map = useMap()
  const nodes = useGraphStore((s) => s.nodes)
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const analysisResult = useGraphStore((s) => s.analysisResult)

  useEffect(() => {
    if (!analysisResult) return

    const betweenness = analysisResult.metrics.betweenness
    const values = Object.values(betweenness)
    const max = values.length ? Math.max(...values) : 0
    if (max === 0) return

    const points = nodes
      .filter((n) => !removedNodes.includes(n.id))
      .map((n): [number, number, number] => {
        const bc = betweenness[n.id] ?? 0
        return [n.lat, n.lon, bc / max]
      })
      .filter((p) => p[2] > 0)

    const layer = L.heatLayer(points, {
      radius: 25,
      blur: 20,
      maxZoom: 17,
      max: 1.0,
      minOpacity: 0.35,
      gradient: {
        0.0: '#3b82f6',
        0.3: '#22c55e',
        0.55: '#eab308',
        0.75: '#f97316',
        1.0: '#ef4444',
      },
    })

    layer.addTo(map)
    return () => {
      map.removeLayer(layer)
    }
  }, [map, nodes, removedNodes, analysisResult])

  return null
}
