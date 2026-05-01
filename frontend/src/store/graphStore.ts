import { create } from 'zustand'
import type { NodeSchema, EdgeSchema } from '../types/graph'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

export type MapMode = 'view' | 'delete' | 'add-edge' | 'add-node' | 'route'
export type ViewMode = 'points' | 'heatmap'

export interface AddedNode {
  id: string
  lat: number
  lon: number
  label: string
  node_type: string
}

export interface FocusTarget {
  id: string
  lat: number
  lon: number
  ts: number
}

export interface RoutePin {
  lat: number
  lon: number
}

export interface RouteResult {
  found: boolean
  path: { id: string; lat: number; lon: number }[]
  distance_km: number
  drive_time_minutes: number
  walk_time_minutes: number
  total_time_minutes: number
  snap_from: { id: string; lat: number; lon: number } | null
  snap_to: { id: string; lat: number; lon: number } | null
  snap_from_distance_km: number
  snap_to_distance_km: number
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
  viewMode: ViewMode
  selectedNodeId: string | null
  routeFrom: RoutePin | null
  routeTo: RoutePin | null
  routeResult: RouteResult | null
  focusTarget: FocusTarget | null
  scenarioMeta: { name: string; description: string | null } | null

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
  setViewMode: (mode: ViewMode) => void
  setSelectedNodeId: (id: string | null) => void
  setRoutePin: (which: 'from' | 'to', pin: RoutePin | null) => void
  setRouteResult: (result: RouteResult | null) => void
  resetRoute: () => void
  focusOnNode: (id: string, lat: number, lon: number) => void
  clearFocus: () => void
  applyCascadeToScenario: () => void
  setScenarioMeta: (name: string, description: string | null) => void
  clearScenarioMeta: () => void
  applyScenario: (s: {
    removed_nodes: string[]
    removed_edges: string[][]
    added_nodes: { id: string; label: string; lat: number; lon: number; node_type?: string }[]
    added_edges: string[][]
  }) => void
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
  viewMode: 'points',
  selectedNodeId: null,
  routeFrom: null,
  routeTo: null,
  routeResult: null,
  focusTarget: null,
  scenarioMeta: null,

  setGraph: (district, nodes, edges) =>
    set({
      district, nodes, edges,
      removedNodes: [], removedEdges: [],
      addedNodes: [], addedEdges: [], addHistory: [],
      analysisResult: null, cascadeResult: null,
      isDirty: false, selectedNodeId: null,
      routeFrom: null, routeTo: null, routeResult: null,
      focusTarget: null, scenarioMeta: null,
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
  setViewMode: (mode) => set({ viewMode: mode }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setRoutePin: (which, pin) =>
    set(which === 'from' ? { routeFrom: pin, routeResult: null } : { routeTo: pin, routeResult: null }),
  setRouteResult: (result) => set({ routeResult: result }),
  resetRoute: () => set({ routeFrom: null, routeTo: null, routeResult: null }),
  focusOnNode: (id, lat, lon) => set({ focusTarget: { id, lat, lon, ts: Date.now() } }),
  clearFocus: () => set({ focusTarget: null }),
  applyCascadeToScenario: () => {
    const { cascadeResult, removedNodes } = get()
    if (!cascadeResult || cascadeResult.steps.length === 0) return
    const ids = cascadeResult.steps.map((s) => s.removed_node_id)
    const merged = Array.from(new Set([...removedNodes, ...ids]))
    set({ removedNodes: merged, cascadeResult: null, isDirty: true })
  },
  setScenarioMeta: (name, description) => set({ scenarioMeta: { name, description } }),
  clearScenarioMeta: () => set({ scenarioMeta: null }),
  applyScenario: (s) => set({
    removedNodes: s.removed_nodes,
    removedEdges: s.removed_edges,
    addedNodes: s.added_nodes.map((n) => ({ ...n, node_type: n.node_type ?? 'other' })),
    addedEdges: s.added_edges,
    addHistory: [],
    isDirty: true,
  }),
}))
