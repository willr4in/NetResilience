export const DEFAULT_CENTER: [number, number] = [55.765, 37.605]
export const DEFAULT_ZOOM = 14
export const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
export const TILE_ATTRIBUTION = '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
export const DISTRICT = 'compare'

// Ограничение области карты — вся Москва с запасом
export const MAP_BOUNDS: [[number, number], [number, number]] = [
  [55.3, 36.8], // юго-запад
  [56.1, 38.2], // северо-восток
]
export const MAP_MIN_ZOOM = 10
