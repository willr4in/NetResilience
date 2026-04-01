import { create } from 'zustand'
import type { Scenario } from '../types/scenario'
import { useGraphStore } from './graphStore'

interface ScenariosState {
  scenarios: Scenario[]
  total: number
  page: number
  pages: number
  setScenarios: (scenarios: Scenario[], total: number, pages: number, page: number) => void
  loadScenario: (scenario: Scenario) => void
}

export const useScenariosStore = create<ScenariosState>((set) => ({
  scenarios: [],
  total: 0,
  page: 1,
  pages: 1,
  setScenarios: (scenarios, total, pages, page) => set({ scenarios, total, pages, page }),
  loadScenario: (scenario: Scenario) => {
    const graphStore = useGraphStore.getState()
    graphStore.resetChanges()
    scenario.removed_nodes.forEach((nodeId) => graphStore.toggleNode(nodeId))
    scenario.removed_edges.forEach(([source, target]) => graphStore.toggleEdge(source, target))
  },
}))
