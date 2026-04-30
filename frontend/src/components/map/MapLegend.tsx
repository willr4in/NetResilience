import { useGraphStore } from '../../store/graphStore'

const POINT_ITEMS = [
  { color: '#3b82f6', label: 'Обычный узел' },
  { color: '#eab308', label: 'Умеренно критичный' },
  { color: '#f97316', label: 'Критичный' },
  { color: '#ef4444', label: 'Очень критичный' },
  { color: '#a855f7', label: 'Изолированный' },
  { color: '#9ca3af', label: 'Удалённый' },
  { color: '#22c55e', label: 'Добавленный' },
  { color: '#10b981', label: 'Маршрут A' },
  { color: '#ef4444', label: 'Маршрут B' },
]

const HEAT_ITEMS = [
  { color: '#3b82f6', label: 'Низкая нагрузка' },
  { color: '#22c55e', label: 'Умеренная' },
  { color: '#eab308', label: 'Повышенная' },
  { color: '#f97316', label: 'Высокая' },
  { color: '#ef4444', label: 'Критическая' },
]

export default function MapLegend() {
  const viewMode = useGraphStore((s) => s.viewMode)
  const items = viewMode === 'heatmap' ? HEAT_ITEMS : POINT_ITEMS
  const title = viewMode === 'heatmap' ? 'Бетвинность' : 'Обозначения'

  return (
    <div className="absolute bottom-16 left-3 z-[1000] bg-white border border-gray-200 rounded-lg shadow px-3 py-2">
      <p className="text-xs font-semibold text-gray-600 mb-1.5">{title}</p>
      <div className="flex flex-col gap-1">
        {items.map(({ color, label }) => (
          <div key={label} className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full shrink-0"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-gray-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
