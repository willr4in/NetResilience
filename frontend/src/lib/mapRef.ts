import type L from 'leaflet'

let instance: L.Map | null = null

export function setMapInstance(m: L.Map | null) {
  instance = m
}

export function getMapInstance(): L.Map | null {
  return instance
}
