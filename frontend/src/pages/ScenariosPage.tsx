import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getScenarios, getPublicScenarios, recordView, deleteScenario } from '../api/scenarios'
import { useScenariosStore } from '../store/scenariosStore'
import { useAuthStore } from '../store/authStore'
import { ROUTES } from '../constants/routes'
import LoadingSpinner from '../components/common/LoadingSpinner'
import type { Scenario } from '../types/scenario'
import { formatDate } from '../utils/formatDate'

type Tab = 'my' | 'public'

function ScenarioCard({
  scenario,
  isOwn,
  onLoad,
  onDelete,
}: {
  scenario: Scenario
  isOwn: boolean
  onLoad: () => void
  onDelete?: () => void
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-start justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-medium text-gray-800 truncate">{scenario.name}</h2>
          {!isOwn && scenario.author_name && (
            <span className="text-xs text-gray-400 shrink-0">{scenario.author_name}</span>
          )}
        </div>
        {scenario.description && (
          <p className="text-xs text-gray-500 mt-0.5 truncate">{scenario.description}</p>
        )}
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-2 text-xs text-gray-400">
          <span>Создан: {formatDate(scenario.created_at)}</span>
          <span>Удалено узлов: {scenario.removed_nodes.length}</span>
          <span>Удалено рёбер: {scenario.removed_edges.length}</span>
          {scenario.added_nodes.length > 0 && <span>Добавлено узлов: {scenario.added_nodes.length}</span>}
          {scenario.added_edges.length > 0 && <span>Добавлено рёбер: {scenario.added_edges.length}</span>}
          <span>Просмотров: {scenario.hits}</span>
        </div>
      </div>

      <div className="flex gap-2 shrink-0">
        <button
          onClick={onLoad}
          className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg transition-colors"
        >
          Загрузить
        </button>
        {isOwn && onDelete && (
          <button
            onClick={onDelete}
            className="bg-white hover:bg-red-50 border border-gray-200 hover:border-red-300 text-gray-500 hover:text-red-500 text-xs px-3 py-1.5 rounded-lg transition-colors"
          >
            Удалить
          </button>
        )}
      </div>
    </div>
  )
}

export default function ScenariosPage() {
  const { scenarios, total, pages, setScenarios } = useScenariosStore()
  const currentUser = useAuthStore((s) => s.user)
  const [tab, setTab] = useState<Tab>('my')
  const [publicScenarios, setPublicScenarios] = useState<Scenario[]>([])
  const [publicTotal, setPublicTotal] = useState(0)
  const [publicPages, setPublicPages] = useState(1)
  const [publicPage, setPublicPage] = useState(1)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const fetchMy = async (p: number) => {
    setIsLoading(true)
    try {
      const { data } = await getScenarios(p)
      setScenarios(data.items, data.total, data.pages, data.page)
      setPage(data.page)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchPublic = async (p: number) => {
    setIsLoading(true)
    try {
      const { data } = await getPublicScenarios(p)
      setPublicScenarios(data.items)
      setPublicTotal(data.total)
      setPublicPages(data.pages)
      setPublicPage(data.page)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { fetchMy(1) }, [])
  useEffect(() => { if (tab === 'public') fetchPublic(1) }, [tab])

  const handleLoad = async (scenario: Scenario) => {
    await recordView(scenario.id).catch(() => {})
    navigate(ROUTES.MAP, { state: { scenario } })
  }

  const handleDelete = async (id: number) => {
    await deleteScenario(id)
    fetchMy(page)
  }

  const activeScenarios = tab === 'my' ? scenarios : publicScenarios
  const activeTotal = tab === 'my' ? total : publicTotal
  const activePages = tab === 'my' ? pages : publicPages
  const activePage = tab === 'my' ? page : publicPage
  const setActivePage = tab === 'my' ? fetchMy : fetchPublic

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-xl font-semibold text-gray-800 mb-4">Сценарии</h1>

      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab('my')}
          className={`px-4 py-1.5 text-sm rounded-md transition-colors ${
            tab === 'my' ? 'bg-white text-gray-800 shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Мои
        </button>
        <button
          onClick={() => setTab('public')}
          className={`px-4 py-1.5 text-sm rounded-md transition-colors ${
            tab === 'public' ? 'bg-white text-gray-800 shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Все сценарии
        </button>
      </div>

      {isLoading && <LoadingSpinner />}

      {!isLoading && activeScenarios.length === 0 && (
        <div className="text-sm text-gray-400 py-12 text-center">
          {tab === 'my'
            ? 'Сохранённых сценариев нет. Перейдите на карту и нажмите «Сохранить».'
            : 'Пока нет публичных сценариев.'}
        </div>
      )}

      <div className="flex flex-col gap-3">
        {activeScenarios.map((scenario) => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            isOwn={scenario.user_id === currentUser?.id}
            onLoad={() => handleLoad(scenario)}
            onDelete={scenario.user_id === currentUser?.id ? () => handleDelete(scenario.id) : undefined}
          />
        ))}
      </div>

      {activePages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          {Array.from({ length: activePages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setActivePage(p)}
              className={`w-8 h-8 text-sm rounded-lg transition-colors ${
                p === activePage
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
        Всего сценариев: {activeTotal}
      </p>
    </div>
  )
}
