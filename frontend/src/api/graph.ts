import client from './client'
import type { GraphSchema, GraphChanges, CascadeRequest } from '../types/graph'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

export const getGraph = (district: string) =>
  client.get<GraphSchema>(`/graph/${district}`)

export const calculate = (changes: GraphChanges) =>
  client.post<GraphAnalysisResponse>('/graph/calculate', changes)

export const simulateCascade = (data: CascadeRequest) =>
  client.post<CascadeResponse>('/graph/simulate-cascade', data)
