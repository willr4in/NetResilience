import client from './client'
import type { HistoryList } from '../types/history'

export const getHistory = (page = 1, size = 10, action = '', search = '') =>
  client.get<HistoryList>('/history', { params: { page, size, action, search } })

export const getScenarioHistory = (scenarioId: number, page = 1, size = 10) =>
  client.get<HistoryList>(`/history/scenario/${scenarioId}`, { params: { page, size } })
