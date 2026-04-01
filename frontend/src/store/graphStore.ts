import { create } from 'zustand'
import type { NodeSchema, EdgeSchema } from '../types/graph'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

interface GraphState {
  district: string
  nodes: NodeSchema[]
  edges: EdgeSchema[]
  removedNodes: string[]
  removedEdges: string[][]
  analysisResult: GraphAnalysisResponse | null
  cascadeResult: CascadeResponse | null
  isLoading: boolean
  isCalculating: boolean

  setGraph: (district: string, nodes: NodeSchema[], edges: EdgeSchema[]) => void
  toggleNode: (nodeId: string) => void
  toggleEdge: (source: string, target: string) => void
  resetChanges: () => void
  setAnalysisResult: (result: GraphAnalysisResponse) => void
  setCascadeResult: (result: CascadeResponse) => void
  setLoading: (value: boolean) => void
  setCalculating: (value: boolean) => void
}

export const useGraphStore = create<GraphState>((set, get) => ({
  district: 'tverskoy',
  nodes: [],
  edges: [],
  removedNodes: [],
  removedEdges: [],
  analysisResult: null,
  cascadeResult: null,
  isLoading: false,
  isCalculating: false,

  setGraph: (district, nodes, edges) =>
    set({ district, nodes, edges, removedNodes: [], removedEdges: [], analysisResult: null, cascadeResult: null }),

  toggleNode: (nodeId) => {
    const { removedNodes } = get()
    const already = removedNodes.includes(nodeId)
    set({ removedNodes: already ? removedNodes.filter((n) => n !== nodeId) : [...removedNodes, nodeId] })
  },

  toggleEdge: (source, target) => {
    const { removedEdges } = get()
    const already = removedEdges.some(([s, t]) => s === source && t === target)
    set({
      removedEdges: already
        ? removedEdges.filter(([s, t]) => !(s === source && t === target))
        : [...removedEdges, [source, target]],
    })
  },

  resetChanges: () =>
    set({ removedNodes: [], removedEdges: [], analysisResult: null, cascadeResult: null }),

  setAnalysisResult: (result) => set({ analysisResult: result }),
  setCascadeResult: (result) => set({ cascadeResult: result }),
  setLoading: (value) => set({ isLoading: value }),
  setCalculating: (value) => set({ isCalculating: value }),
}))
