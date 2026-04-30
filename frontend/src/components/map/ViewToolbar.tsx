import { useGraphStore, type ViewMode } from '../../store/graphStore'

interface ViewButton {
  mode: ViewMode
  label: string
  icon: React.ReactNode
}

const VIEWS: ViewButton[] = [
  {
    mode: 'points',
    label: 'Узлы и рёбра',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <circle cx="6" cy="6" r="2" />
        <circle cx="18" cy="6" r="2" />
        <circle cx="12" cy="18" r="2" />
        <path d="M7 7l4 10M17 7l-4 10" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    mode: 'heatmap',
    label: 'Тепловая карта по бетвинности (нужен расчёт метрик)',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <path d="M12 2C9 6 9 8 12 11s3 5 0 9" strokeLinecap="round" />
        <path d="M7 6c-2 3-2 5 0 7s2 4 0 7" strokeLinecap="round" />
        <path d="M17 6c2 3 2 5 0 7s-2 4 0 7" strokeLinecap="round" />
      </svg>
    ),
  },
]

export default function ViewToolbar() {
  const viewMode = useGraphStore((s) => s.viewMode)
  const setViewMode = useGraphStore((s) => s.setViewMode)
  const analysisResult = useGraphStore((s) => s.analysisResult)
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const mapMode = useGraphStore((s) => s.mapMode)
  const routeFrom = useGraphStore((s) => s.routeFrom)
  const routeTo = useGraphStore((s) => s.routeTo)
  const heatmapDisabled = !analysisResult
  const sidebarOpen = !!analysisResult || !!cascadeResult || mapMode === 'route' || !!routeFrom || !!routeTo

  return (
    <div
      className={`absolute bottom-3 z-[1001] flex flex-col gap-1 bg-white/90 backdrop-blur rounded-lg border border-gray-200 shadow p-1 transition-[right] duration-300 ease-in-out ${
        sidebarOpen ? 'right-[332px]' : 'right-3'
      }`}
    >
      {VIEWS.map(({ mode, label, icon }) => {
        const disabled = mode === 'heatmap' && heatmapDisabled
        const active = viewMode === mode
        return (
          <button
            key={mode}
            title={disabled ? 'Сначала нажмите «Рассчитать», чтобы получить метрики' : label}
            disabled={disabled}
            onClick={() => setViewMode(mode)}
            className={`w-8 h-8 flex items-center justify-center rounded transition-colors ${
              active
                ? 'bg-blue-600 text-white'
                : disabled
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {icon}
          </button>
        )
      })}
    </div>
  )
}
