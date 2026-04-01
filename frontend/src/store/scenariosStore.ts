import { create } from 'zustand'
import type { Scenario } from '../types/scenario'

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
  loadScenario: () => {},
}))
