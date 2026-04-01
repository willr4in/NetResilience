import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useGraphStore } from '../store/graphStore'
import { getGraph, calculate } from '../api/graph'
import { createScenario } from '../api/scenarios'
import { extractChanges } from '../utils/normalizeGraphData'
import { DISTRICT } from '../constants/map'
import GraphMap from '../components/map/GraphMap'
import MapControls from '../components/map/MapControls'
import Sidebar from '../components/layout/Sidebar'
import ResiliencePanel from '../components/panels/ResiliencePanel'
import MetricsPanel from '../components/panels/MetricsPanel'
import CriticalNodes from '../components/panels/CriticalNodes'
import CascadePanel from '../components/panels/CascadePanel'
import LoadingSpinner from '../components/common/LoadingSpinner'
import type { GraphSchema } from '../types/graph'

export default function MapPage() {
  const { setGraph, setAnalysisResult, setCalculating, setLoading } = useGraphStore()
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const analysisResult = useGraphStore((s) => s.analysisResult)
  const isLoading = useGraphStore((s) => s.isLoading)
  const location = useLocation()

  const [graphSchema, setGraphSchema] = useState<GraphSchema | null>(null)
  const [saveModalOpen, setSaveModalOpen] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [saveError, setSaveError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const { data } = await getGraph(DISTRICT)
        setGraphSchema(data)
        setGraph(data.metadata.district, data.nodes, data.edges)
        const scenario = location.state?.scenario
        if (scenario) {
          scenario.removed_nodes.forEach((id: string) => useGraphStore.getState().toggleNode(id))
          scenario.removed_edges.forEach(([s, t]: string[]) => useGraphStore.getState().toggleEdge(s, t))
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleCalculate = async () => {
    if (!graphSchema) return
    setCalculating(true)
    try {
      const changes = extractChanges(graphSchema, removedNodes, removedEdges)
      const { data } = await calculate(changes)
      setAnalysisResult(data)
    } finally {
      setCalculating(false)
    }
  }

  const handleSave = async () => {
    if (!graphSchema || !saveName.trim()) return
    setSaveError('')
    try {
      await createScenario({
        name: saveName.trim(),
        district: graphSchema.metadata.district,
        removed_nodes: removedNodes,
        removed_edges: removedEdges,
        added_nodes: [],
        added_edges: [],
      })
      setSaveModalOpen(false)
      setSaveName('')
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setSaveError(detail.map((e: any) => e.msg).join(', '))
      } else if (typeof detail === 'string') {
        setSaveError(detail)
      } else {
        setSaveError('Ошибка при сохранении')
      }
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <LoadingSpinner text="Загрузка графа..." />
      </div>
    )
  }

  return (
    <div className="flex h-full relative">
      <div className="flex-1 relative">
        <GraphMap />
        <MapControls
          onCalculate={handleCalculate}
          onSave={() => setSaveModalOpen(true)}
        />
      </div>

      <Sidebar>
        {analysisResult && (
          <>
            <ResiliencePanel resilience={analysisResult.resilience} />
            <MetricsPanel metrics={analysisResult.metrics} />
            <CriticalNodes
              criticalNodes={analysisResult.metrics.critical_nodes}
              betweenness={analysisResult.metrics.betweenness}
            />
          </>
        )}
        <CascadePanel />
      </Sidebar>

      {saveModalOpen && (
        <div className="absolute inset-0 z-[2000] flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-lg p-6 w-80">
            <h2 className="text-base font-semibold text-gray-800 mb-4">Сохранить сценарий</h2>
            <input
              type="text"
              placeholder="Название сценария"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {saveError && <p className="text-xs text-red-500 mb-3">{saveError}</p>}
            {!saveError && <div className="mb-3" />}
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setSaveModalOpen(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
              >
                Отмена
              </button>
              <button
                onClick={handleSave}
                disabled={!saveName.trim()}
                className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
