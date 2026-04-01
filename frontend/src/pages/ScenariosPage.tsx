import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getScenarios, deleteScenario } from '../api/scenarios'
import { useScenariosStore } from '../store/scenariosStore'
import { ROUTES } from '../constants/routes'
import LoadingSpinner from '../components/common/LoadingSpinner'
import type { Scenario } from '../types/scenario'
import { formatDate } from '../utils/formatDate'

export default function ScenariosPage() {
  const { scenarios, total, pages, setScenarios } = useScenariosStore()
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const fetchScenarios = async (p: number) => {
    setIsLoading(true)
    try {
      const { data } = await getScenarios(p)
      setScenarios(data.items, data.total, data.pages, data.page)
      setPage(data.page)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { fetchScenarios(1) }, [])

  const handleLoad = (scenario: Scenario) => {
    navigate(ROUTES.MAP, { state: { scenario } })
  }

  const handleDelete = async (id: number) => {
    await deleteScenario(id)
    fetchScenarios(page)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Сценарии</h1>

      {isLoading && <LoadingSpinner />}

      {!isLoading && scenarios.length === 0 && (
        <div className="text-sm text-gray-400 py-12 text-center">
          Сохранённых сценариев нет. Перейдите на карту и нажмите «Сохранить».
        </div>
      )}

      <div className="flex flex-col gap-3">
        {scenarios.map((scenario) => (
          <div
            key={scenario.id}
            className="bg-white rounded-xl border border-gray-200 p-4 flex items-start justify-between gap-4"
          >
            <div className="flex-1 min-w-0">
              <h2 className="text-sm font-medium text-gray-800 truncate">{scenario.name}</h2>
              {scenario.description && (
                <p className="text-xs text-gray-500 mt-0.5 truncate">{scenario.description}</p>
              )}
              <div className="flex gap-4 mt-2 text-xs text-gray-400">
                <span>Создан: {formatDate(scenario.created_at)}</span>
                <span>Удалено узлов: {scenario.removed_nodes.length}</span>
                <span>Удалено рёбер: {scenario.removed_edges.length}</span>
                <span>Просмотров: {scenario.hits}</span>
              </div>
            </div>

            <div className="flex gap-2 shrink-0">
              <button
                onClick={() => handleLoad(scenario)}
                className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg transition-colors"
              >
                Загрузить
              </button>
              <button
                onClick={() => handleDelete(scenario.id)}
                className="bg-white hover:bg-red-50 border border-gray-200 hover:border-red-300 text-gray-500 hover:text-red-500 text-xs px-3 py-1.5 rounded-lg transition-colors"
              >
                Удалить
              </button>
            </div>
          </div>
        ))}
      </div>

      {pages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => fetchScenarios(p)}
              className={`w-8 h-8 text-sm rounded-lg transition-colors ${
                p === page
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-4 text-center">
        Всего сценариев: {total}
      </p>
    </div>
  )
}
