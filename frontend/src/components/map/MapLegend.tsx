const LEGEND_ITEMS = [
  { color: '#3b82f6', label: 'Обычный узел' },
  { color: '#eab308', label: 'Умеренно критичный' },
  { color: '#f97316', label: 'Критичный' },
  { color: '#ef4444', label: 'Очень критичный' },
  { color: '#a855f7', label: 'Изолированный' },
  { color: '#9ca3af', label: 'Удалённый' },
  { color: '#22c55e', label: 'Добавленный' },
]

export default function MapLegend() {
  return (
    <div className="absolute bottom-16 left-3 z-[1000] bg-white border border-gray-200 rounded-lg shadow px-3 py-2">
      <p className="text-xs font-semibold text-gray-600 mb-1.5">Обозначения</p>
      <div className="flex flex-col gap-1">
        {LEGEND_ITEMS.map(({ color, label }) => (
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
