export interface Scenario {
  id: number
  user_id: number
  name: string
  description: string | null
  district: string
  removed_nodes: string[]
  removed_edges: string[][]
  added_nodes: { id: string; label: string; lat: number; lon: number }[]
  added_edges: string[][]
  metrics: Record<string, unknown> | null
  author_name: string | null
  hits: number
  created_at: string
  last_used_at: string
}

export interface ScenarioCreate {
  name: string
  description?: string
  district: string
  removed_nodes: string[]
  removed_edges: string[][]
  added_nodes: { id: string; label: string; lat: number; lon: number }[]
  added_edges: string[][]
}

export interface ScenarioUpdate {
  name?: string
  description?: string
}

export interface ScenarioList {
  items: Scenario[]
  total: number
  page: number
  size: number
  pages: number
}
