export interface MetricResponse {
  betweenness: Record<string, number>
  closeness: Record<string, number>
  degree: Record<string, number>
  critical_nodes: string[]
  isolated_nodes: string[]
}

export interface ResilienceComparison {
  resilience_score_before: number
  resilience_score_after: number
  resilience_delta: number
  avg_path_before: number | null
  avg_path_after: number | null
  avg_path_delta: number | null
  top_nodes_change: {
    top_before: string[]
    top_after: string[]
    new_critical: string[]
    no_longer_critical: string[]
  }
}

export interface ResilienceMetrics {
  connected: boolean
  largest_component_ratio: number
  average_shortest_path: number | null
  betweenness_concentration: number
  resilience_score: number
  comparison: ResilienceComparison | null
}

export interface GraphAnalysisResponse {
  metrics: MetricResponse
  resilience: ResilienceMetrics
  calculation_time_ms: number
}

export interface CascadeStep {
  step: number
  removed_node_id: string
  removed_node_label: string
  resilience_score: number
  connected: boolean
  largest_component_ratio: number
  betweenness_concentration: number
}

export interface CascadeResponse {
  district: string
  initial_resilience_score: number
  steps: CascadeStep[]
  total_steps: number
  calculation_time_ms: number
}
