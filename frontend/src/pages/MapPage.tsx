import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import axios from 'axios'
import { useGraphStore } from '../store/graphStore'
import { getGraph, calculate, simulateCascade, findRoute } from '../api/graph'
import { isAbortError } from '../api/client'
import { createScenario } from '../api/scenarios'
import { extractChanges } from '../utils/normalizeGraphData'
import { DISTRICT } from '../constants/map'
import GraphMap from '../components/map/GraphMap'
import MapControls from '../components/map/MapControls'
import ModeToolbar from '../components/map/ModeToolbar'
import ViewToolbar from '../components/map/ViewToolbar'
import MapLegend from '../components/map/MapLegend'
import Sidebar from '../components/layout/Sidebar'
import ResiliencePanel from '../components/panels/ResiliencePanel'
import MetricsPanel from '../components/panels/MetricsPanel'
import CriticalNodes from '../components/panels/CriticalNodes'
import CascadePanel from '../components/panels/CascadePanel'
import RoutePanel from '../components/panels/RoutePanel'
import MapSkeleton from '../components/common/MapSkeleton'
import { exportScenarioPdf } from '../utils/exportPdf'
import type { GraphSchema } from '../types/graph'
import type { Scenario } from '../types/scenario'

export default function MapPage() {
  const { setGraph, setAnalysisResult, setCascadeResult, setCalculating, setLoading, setScenarioMeta, applyScenario } = useGraphStore()
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const addedNodes = useGraphStore((s) => s.addedNodes)
  const addedEdges = useGraphStore((s) => s.addedEdges)
  const analysisResult = useGraphStore((s) => s.analysisResult)
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const isLoading = useGraphStore((s) => s.isLoading)
  const mapMode = useGraphStore((s) => s.mapMode)
  const routeFrom = useGraphStore((s) => s.routeFrom)
  const routeTo = useGraphStore((s) => s.routeTo)
  const setRouteResult = useGraphStore((s) => s.setRouteResult)
  const scenarioMeta = useGraphStore((s) => s.scenarioMeta)
  const location = useLocation()

  const [graphSchema, setGraphSchema] = useState<GraphSchema | null>(null)
  const [saveModalOpen, setSaveModalOpen] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [saveDescription, setSaveDescription] = useState('')
  const [saveError, setSaveError] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isRouting, setIsRouting] = useState(false)
  const [isExporting, setIsExporting] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const { data } = await getGraph(DISTRICT)
        setGraphSchema(data)
        setGraph(data.metadata.district, data.nodes, data.edges)
        const scenario = location.state?.scenario as Scenario | undefined
        if (scenario) {
          applyScenario(scenario)
          setScenarioMeta(scenario.name, scenario.description ?? null)

          setCalculating(true)
          try {
            const { removedNodes, removedEdges, addedNodes, addedEdges } = useGraphStore.getState()
            const changes = extractChanges(data, removedNodes, removedEdges, addedNodes, addedEdges)
            const { data: result } = await calculate(changes)
            setAnalysisResult(result)
          } catch (err) {
            if (!isAbortError(err)) throw err
          } finally {
            setCalculating(false)
          }
        }
      } catch (err) {
        if (!isAbortError(err)) throw err
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
      const changes = extractChanges(graphSchema, removedNodes, removedEdges, addedNodes, addedEdges)
      const { data } = await calculate(changes)
      setAnalysisResult(data)
    } catch (err) {
      if (!isAbortError(err)) throw err
    } finally {
      setCalculating(false)
    }
  }

  const handleCascade = async (steps: number) => {
    setCalculating(true)
    try {
      const { data } = await simulateCascade({
        district: DISTRICT,
        steps,
        removed_nodes: removedNodes,
        removed_edges: removedEdges,
        added_nodes: addedNodes,
        added_edges: addedEdges,
      })
      setCascadeResult(data)
    } catch (err) {
      if (!isAbortError(err)) throw err
    } finally {
      setCalculating(false)
    }
  }

  const handleBuildRoute = async () => {
    if (!routeFrom || !routeTo) return
    setIsRouting(true)
    try {
      const { data } = await findRoute({
        district: DISTRICT,
        from_lat: routeFrom.lat,
        from_lon: routeFrom.lon,
        to_lat: routeTo.lat,
        to_lon: routeTo.lon,
        removed_nodes: removedNodes,
        removed_edges: removedEdges,
        added_nodes: addedNodes,
        added_edges: addedEdges,
      })
      setRouteResult({
        found: data.found,
        path: data.path,
        distance_km: data.distance_km,
        drive_time_minutes: data.drive_time_minutes,
        walk_time_minutes: data.walk_time_minutes,
        total_time_minutes: data.total_time_minutes,
        snap_from: data.snap_from,
        snap_to: data.snap_to,
        snap_from_distance_km: data.snap_from_distance_km,
        snap_to_distance_km: data.snap_to_distance_km,
      })
    } catch (err) {
      if (!isAbortError(err)) throw err
    } finally {
      setIsRouting(false)
    }
  }

  const handleSave = async () => {
    if (!graphSchema || !saveName.trim() || isSaving) return
    setSaveError('')
    if (saveName.trim().length < 3) {
      setSaveError('Название должно содержать минимум 3 символа')
      return
    }
    if (saveName.trim().length > 100) {
      setSaveError('Название не должно превышать 100 символов')
      return
    }
    setIsSaving(true)
    try {
      await createScenario({
        name: saveName.trim(),
        description: saveDescription.trim() || undefined,
        district: graphSchema.metadata.district,
        removed_nodes: removedNodes,
        removed_edges: removedEdges,
        added_nodes: addedNodes,
        added_edges: addedEdges,
      })
      setSaveModalOpen(false)
      setSaveName('')
      setSaveDescription('')
    } catch (err) {
      const detail = axios.isAxiosError(err) ? err.response?.data?.detail : undefined
      if (Array.isArray(detail)) {
        setSaveError(detail.map((e: Record<string, unknown>) => String(e.msg)).join(', '))
      } else if (typeof detail === 'string') {
        setSaveError(detail)
      } else {
        setSaveError('Ошибка при сохранении')
      }
    } finally {
      setIsSaving(false)
    }
  }

  const handleExportPdf = async () => {
    if (!graphSchema || !analysisResult || !scenarioMeta || isExporting) return
    setIsExporting(true)
    try {
      await exportScenarioPdf({
        scenarioName: scenarioMeta.name,
        description: scenarioMeta.description,
        district: graphSchema.metadata.district,
        analysis: analysisResult,
        cascade: cascadeResult,
        removedCount: removedNodes.length + removedEdges.length,
        addedCount: addedNodes.length + addedEdges.length,
      })
    } catch (e) {
      console.error('PDF export failed:', e)
    } finally {
      setIsExporting(false)
    }
  }

  if (isLoading) {
    return <MapSkeleton />
  }

  return (
    <div className="h-full relative overflow-hidden">
      <GraphMap />
      <ModeToolbar />
      <ViewToolbar />
      <MapLegend />
      <MapControls
        onCalculate={handleCalculate}
        onCascade={handleCascade}
        onSave={() => setSaveModalOpen(true)}
      />

      <Sidebar visible={!!analysisResult || !!cascadeResult || mapMode === 'route' || !!routeFrom || !!routeTo}>
        <RoutePanel onBuild={handleBuildRoute} isBuilding={isRouting} />
        {analysisResult && (
          <>
            <ResiliencePanel resilience={analysisResult.resilience} />
            <MetricsPanel metrics={analysisResult.metrics} />
            <CriticalNodes
              criticalNodes={analysisResult.metrics.critical_nodes}
              betweenness={analysisResult.metrics.betweenness}
            />
            <p className="text-xs text-gray-400 text-right px-4 py-2">
              Рассчитано за {analysisResult.calculation_time_ms.toFixed(0)} мс
            </p>
          </>
        )}
        <CascadePanel />
        {analysisResult && scenarioMeta && (
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={handleExportPdf}
              disabled={isExporting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {isExporting ? 'Формируется PDF…' : 'Скачать PDF-отчёт'}
            </button>
          </div>
        )}
      </Sidebar>

      {saveModalOpen && (
        <div className="absolute inset-0 z-[2000] flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-lg p-6 w-96">
            <h2 className="text-base font-semibold text-gray-800 mb-4">Сохранить сценарий</h2>
            <input
              type="text"
              placeholder="Название сценария"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              disabled={isSaving}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
            />
            <textarea
              placeholder="Краткое описание (необязательно)"
              value={saveDescription}
              onChange={(e) => setSaveDescription(e.target.value)}
              disabled={isSaving}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-1 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-50"
            />
            {saveError && <p className="text-xs text-red-500 mb-3">{saveError}</p>}
            {!saveError && <div className="mb-3" />}
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setSaveModalOpen(false)}
                disabled={isSaving}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:text-gray-300"
              >
                Отмена
              </button>
              <button
                onClick={handleSave}
                disabled={!saveName.trim() || isSaving}
                className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                {isSaving ? 'Сохранение…' : 'Сохранить'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
