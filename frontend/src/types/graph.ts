export interface GraphMetadata {
  name: string
  city: string
  district: string
}

export interface NodeSchema {
  id: string
  label: string
  lat: number
  lon: number
}

export interface EdgeSchema {
  source: string
  target: string
  weight: number
}

export interface GraphSchema {
  metadata: GraphMetadata
  nodes: NodeSchema[]
  edges: EdgeSchema[]
}

export interface GraphChanges {
  district: string
  removed_nodes: string[]
  removed_edges: string[][]
  added_nodes: NodeSchema[]
  added_edges: string[][]
}

export interface CascadeRequest {
  district: string
  steps: number
  removed_nodes?: string[]
  removed_edges?: string[][]
  added_nodes?: { id: string; label: string; lat: number; lon: number; node_type?: string }[]
  added_edges?: string[][]
}

export interface RouteRequest {
  district: string
  from_lat: number
  from_lon: number
  to_lat: number
  to_lon: number
  removed_nodes?: string[]
  removed_edges?: string[][]
  added_nodes?: { id: string; label: string; lat: number; lon: number; node_type?: string }[]
  added_edges?: string[][]
}

export interface RoutePoint {
  id: string
  lat: number
  lon: number
}

export interface RouteResponse {
  district: string
  found: boolean
  path: RoutePoint[]
  distance_km: number
  drive_time_minutes: number
  walk_time_minutes: number
  total_time_minutes: number
  snap_from: RoutePoint | null
  snap_to: RoutePoint | null
  snap_from_distance_km: number
  snap_to_distance_km: number
  calculation_time_ms: number
}
