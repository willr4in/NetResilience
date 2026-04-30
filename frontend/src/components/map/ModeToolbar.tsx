import { useGraphStore, type MapMode } from '../../store/graphStore'

interface ModeButton {
  mode: MapMode
  label: string
  icon: React.ReactNode
}

const MODES: ModeButton[] = [
  {
    mode: 'view',
    label: 'Просмотр',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <path d="M15 3l-4 4-4-4M4 17l4-4 4 4" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M12 7v10" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    mode: 'delete',
    label: 'Удаление узлов / рёбер',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    mode: 'add-node',
    label: 'Добавить узел (клик по карте)',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    mode: 'add-edge',
    label: 'Добавить ребро (два клика по узлам)',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <circle cx="5" cy="19" r="2" />
        <circle cx="19" cy="5" r="2" />
        <path d="M7 17L17 7" strokeLinecap="round" />
        <path d="M14 5h4v4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    mode: 'route',
    label: 'Маршрут A → B (клик по карте — точка отправления, второй клик — назначение)',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
        <circle cx="6" cy="6" r="2" />
        <circle cx="18" cy="18" r="2" />
        <path d="M8 6h8a3 3 0 0 1 0 6H8a3 3 0 0 0 0 6h8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
]

export default function ModeToolbar() {
  const mapMode = useGraphStore((s) => s.mapMode)
  const setMapMode = useGraphStore((s) => s.setMapMode)
  const undoLastAdd = useGraphStore((s) => s.undoLastAdd)
  const addHistory = useGraphStore((s) => s.addHistory)

  const canUndo = addHistory.length > 0

  return (
    <div className="absolute top-20 left-3 z-[1000] flex flex-col gap-1">
      {MODES.map(({ mode, label, icon }) => (
        <button
          key={mode}
          title={label}
          onClick={() => setMapMode(mode)}
          className={`w-8 h-8 flex items-center justify-center rounded shadow transition-colors ${
            mapMode === mode
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-300'
          }`}
        >
          {icon}
        </button>
      ))}

      <div className="h-px bg-gray-200 mx-1 my-0.5" />
      <button
        title="Отменить последнее добавление"
        onClick={undoLastAdd}
        disabled={!canUndo}
        className={`w-8 h-8 flex items-center justify-center rounded shadow transition-colors border ${
          canUndo
            ? 'bg-white text-gray-600 hover:bg-amber-50 hover:text-amber-600 border-gray-300'
            : 'bg-white text-gray-300 border-gray-200 cursor-not-allowed'
        }`}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
          <path d="M9 14L4 9l5-5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M4 9h11a6 6 0 0 1 0 12h-1" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  )
}
