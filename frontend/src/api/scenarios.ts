import client from './client'
import type { Scenario, ScenarioCreate, ScenarioUpdate, ScenarioList } from '../types/scenario'

export const getScenarios = (page = 1, size = 10) =>
  client.get<ScenarioList>('/scenarios', { params: { page, size } })

export const getScenario = (id: number) =>
  client.get<Scenario>(`/scenarios/${id}`)

export const createScenario = (data: ScenarioCreate) =>
  client.post<Scenario>('/scenarios', data)

export const updateScenario = (id: number, data: ScenarioUpdate) =>
  client.put<Scenario>(`/scenarios/${id}`, data)

export const deleteScenario = (id: number) =>
  client.delete(`/scenarios/${id}`)
