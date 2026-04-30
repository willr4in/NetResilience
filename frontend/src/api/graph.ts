import client, { abortable } from './client'
import type { GraphSchema, GraphChanges, CascadeRequest, RouteRequest, RouteResponse } from '../types/graph'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

export const getGraph = (district: string) =>
  client.get<GraphSchema>(`/graph/${district}`, abortable('graph:get'))

export const calculate = (changes: GraphChanges) =>
  client.post<GraphAnalysisResponse>('/graph/calculate', changes, abortable('graph:calculate'))

export const simulateCascade = (data: CascadeRequest) =>
  client.post<CascadeResponse>('/graph/simulate-cascade', data, abortable('graph:cascade'))

export const findRoute = (data: RouteRequest) =>
  client.post<RouteResponse>('/graph/route', data, abortable('graph:route'))
