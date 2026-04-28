import { create } from 'zustand'
import type { NodeSchema, EdgeSchema } from '../types/graph'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

export type MapMode = 'view' | 'delete' | 'add-edge' | 'add-node'

export interface AddedNode {
  id: string
  lat: number
  lon: number
  label: string
  node_type: string
}

type AddHistoryEntry =
  | { type: 'node'; id: string }
  | { type: 'edge'; source: string; target: string }

interface GraphState {
  district: string
  nodes: NodeSchema[]
  edges: EdgeSchema[]
  removedNodes: string[]
  removedEdges: string[][]
  addedNodes: AddedNode[]
  addedEdges: string[][]
  addHistory: AddHistoryEntry[]
  analysisResult: GraphAnalysisResponse | null
  cascadeResult: CascadeResponse | null
  isLoading: boolean
  isCalculating: boolean
  isDirty: boolean
  mapMode: MapMode
  selectedNodeId: string | null

  setGraph: (district: string, nodes: NodeSchema[], edges: EdgeSchema[]) => void
  toggleNode: (nodeId: string) => void
  toggleEdge: (source: string, target: string) => void
  addNode: (node: AddedNode) => void
  addEdge: (source: string, target: string) => void
  undoLastAdd: () => void
  resetChanges: () => void
  setAnalysisResult: (result: GraphAnalysisResponse | null) => void
  setCascadeResult: (result: CascadeResponse | null) => void
  setLoading: (value: boolean) => void
  setCalculating: (value: boolean) => void
  setMapMode: (mode: MapMode) => void
  setSelectedNodeId: (id: string | null) => void
}

export const useGraphStore = create<GraphState>((set, get) => ({
  district: 'compare',
  nodes: [],
  edges: [],
  removedNodes: [],
  removedEdges: [],
  addedNodes: [],
  addedEdges: [],
  addHistory: [],
  analysisResult: null,
  cascadeResult: null,
  isLoading: false,
  isCalculating: false,
  isDirty: false,
  mapMode: 'view',
  selectedNodeId: null,

  setGraph: (district, nodes, edges) =>
    set({
      district, nodes, edges,
      removedNodes: [], removedEdges: [],
      addedNodes: [], addedEdges: [], addHistory: [],
      analysisResult: null, cascadeResult: null,
      isDirty: false, selectedNodeId: null,
    }),

  toggleNode: (nodeId) => {
    const { removedNodes } = get()
    const already = removedNodes.includes(nodeId)
    set({
      removedNodes: already ? removedNodes.filter((n) => n !== nodeId) : [...removedNodes, nodeId],
      isDirty: true,
    })
  },

  toggleEdge: (source, target) => {
    const { removedEdges } = get()
    const already = removedEdges.some(([s, t]) => s === source && t === target)
    set({
      removedEdges: already
        ? removedEdges.filter(([s, t]) => !(s === source && t === target))
        : [...removedEdges, [source, target]],
      isDirty: true,
    })
  },

  addNode: (node) => {
    set((state) => ({
      addedNodes: [...state.addedNodes, node],
      addHistory: [...state.addHistory, { type: 'node', id: node.id }],
      isDirty: true,
    }))
  },

  addEdge: (source, target) => {
    set((state) => ({
      addedEdges: [...state.addedEdges, [source, target]],
      addHistory: [...state.addHistory, { type: 'edge', source, target }],
      isDirty: true,
    }))
  },

  undoLastAdd: () => {
    const { addHistory, addedNodes, addedEdges } = get()
    if (addHistory.length === 0) return
    const last = addHistory[addHistory.length - 1]
    const newHistory = addHistory.slice(0, -1)
    if (last.type === 'node') {
      set({ addedNodes: addedNodes.filter((n) => n.id !== last.id), addHistory: newHistory, isDirty: true })
    } else {
      set({
        addedEdges: addedEdges.filter(([s, t]) => !(s === last.source && t === last.target)),
        addHistory: newHistory,
        isDirty: true,
      })
    }
  },

  resetChanges: () =>
    set({
      removedNodes: [], removedEdges: [],
      addedNodes: [], addedEdges: [], addHistory: [],
      analysisResult: null, cascadeResult: null,
      isDirty: false, selectedNodeId: null,
    }),

  setAnalysisResult: (result) => set({ analysisResult: result, isDirty: false }),
  setCascadeResult: (result) => set({ cascadeResult: result }),
  setLoading: (value) => set({ isLoading: value }),
  setCalculating: (value) => set({ isCalculating: value }),
  setMapMode: (mode) => set({ mapMode: mode, selectedNodeId: null }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
}))
