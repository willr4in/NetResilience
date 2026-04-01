export type ActionType = 'calculate' | 'save' | 'delete' | 'view'

export interface HistoryRecord {
  id: number
  user_id: number
  scenario_id: number | null
  scenario_name: string | null
  action: ActionType
  details: Record<string, unknown>
  calculation_time_ms: number | null
  created_at: string
}

export interface HistoryList {
  items: HistoryRecord[]
  total: number
  page: number
  size: number
  pages: number
}
