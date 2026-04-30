import { CircleMarker, Polyline, Tooltip } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'

const PIN_FROM_COLOR = '#10b981'
const PIN_TO_COLOR = '#ef4444'
const SNAP_COLOR = '#9ca3af'
const ROUTE_COLOR = '#2563eb'

export default function RouteLayer() {
  const routeFrom = useGraphStore((s) => s.routeFrom)
  const routeTo = useGraphStore((s) => s.routeTo)
  const result = useGraphStore((s) => s.routeResult)

  const polylinePath = result?.found
    ? result.path.map((p) => [p.lat, p.lon] as [number, number])
    : null

  return (
    <>
      {polylinePath && (
        <Polyline
          positions={polylinePath}
          pathOptions={{ color: ROUTE_COLOR, weight: 5, opacity: 0.85 }}
        />
      )}

      {routeFrom && result?.snap_from && (
        <Polyline
          positions={[
            [routeFrom.lat, routeFrom.lon],
            [result.snap_from.lat, result.snap_from.lon],
          ]}
          pathOptions={{ color: SNAP_COLOR, weight: 2, opacity: 0.7, dashArray: '4 6' }}
        />
      )}
      {routeTo && result?.snap_to && (
        <Polyline
          positions={[
            [routeTo.lat, routeTo.lon],
            [result.snap_to.lat, result.snap_to.lon],
          ]}
          pathOptions={{ color: SNAP_COLOR, weight: 2, opacity: 0.7, dashArray: '4 6' }}
        />
      )}

      {routeFrom && (
        <CircleMarker
          center={[routeFrom.lat, routeFrom.lon]}
          radius={8}
          pathOptions={{ color: '#fff', weight: 2, fillColor: PIN_FROM_COLOR, fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -6]}>A — точка отправления</Tooltip>
        </CircleMarker>
      )}
      {routeTo && (
        <CircleMarker
          center={[routeTo.lat, routeTo.lon]}
          radius={8}
          pathOptions={{ color: '#fff', weight: 2, fillColor: PIN_TO_COLOR, fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -6]}>B — точка назначения</Tooltip>
        </CircleMarker>
      )}
    </>
  )
}
