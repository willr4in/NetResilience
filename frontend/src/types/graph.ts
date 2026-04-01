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
}
