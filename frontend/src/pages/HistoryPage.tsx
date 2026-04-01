import { useEffect, useState } from 'react'
import { getHistory } from '../api/history'
import type { HistoryRecord, ActionType } from '../types/history'
import { formatDateTime } from '../utils/formatDate'
import LoadingSpinner from '../components/common/LoadingSpinner'

const ACTION_LABELS: Record<ActionType, string> = {
  calculate: 'Расчёт',
  save: 'Сохранение',
  delete: 'Удаление',
  view: 'Просмотр',
}

const ACTION_COLORS: Record<ActionType, string> = {
  calculate: 'bg-blue-100 text-blue-700',
  save: 'bg-green-100 text-green-700',
  delete: 'bg-red-100 text-red-500',
  view: 'bg-gray-100 text-gray-600',
}

function HistoryItem({ record }: { record: HistoryRecord }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-4">
      <span className={`text-xs font-medium px-2 py-1 rounded-md shrink-0 ${ACTION_COLORS[record.action]}`}>
        {ACTION_LABELS[record.action]}
      </span>

      <div className="flex-1 min-w-0">
        {record.scenario_name && (
          <p className="text-sm text-gray-700 truncate">{record.scenario_name}</p>
        )}
        <p className="text-xs text-gray-400 mt-0.5">{formatDateTime(record.created_at)}</p>
      </div>

      {record.calculation_time_ms != null && (
        <span className="text-xs text-gray-400 shrink-0">
          {record.calculation_time_ms.toFixed(0)} мс
        </span>
      )}
    </div>
  )
}

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)

  const fetchHistory = async (p: number) => {
    setIsLoading(true)
    try {
      const { data } = await getHistory(p)
      setRecords(data.items)
      setTotal(data.total)
      setPage(data.page)
      setPages(data.pages)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { fetchHistory(1) }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">История действий</h1>

      {isLoading && <LoadingSpinner />}

      {!isLoading && records.length === 0 && (
        <div className="text-sm text-gray-400 py-12 text-center">
          История пуста. Начните работу с графом на странице карты.
        </div>
      )}

      <div className="flex flex-col gap-2">
        {records.map((record) => (
          <HistoryItem key={record.id} record={record} />
        ))}
      </div>

      {pages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => fetchHistory(p)}
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
        Всего записей: {total}
      </p>
    </div>
  )
}
