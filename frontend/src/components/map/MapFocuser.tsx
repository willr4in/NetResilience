import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import { useGraphStore } from '../../store/graphStore'

export default function MapFocuser() {
  const map = useMap()
  const focusTarget = useGraphStore((s) => s.focusTarget)

  useEffect(() => {
    if (!focusTarget) return
    map.flyTo([focusTarget.lat, focusTarget.lon], 17, { duration: 0.8 })
  }, [focusTarget, map])

  return null
}
