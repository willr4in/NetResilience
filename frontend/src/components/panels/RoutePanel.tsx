import { useGraphStore } from '../../store/graphStore'

interface Props {
  onBuild: () => void
  isBuilding: boolean
}

export default function RoutePanel({ onBuild, isBuilding }: Props) {
  const routeFrom = useGraphStore((s) => s.routeFrom)
  const routeTo = useGraphStore((s) => s.routeTo)
  const result = useGraphStore((s) => s.routeResult)
  const resetRoute = useGraphStore((s) => s.resetRoute)
  const mapMode = useGraphStore((s) => s.mapMode)

  if (mapMode !== 'route' && !routeFrom && !routeTo && !result) return null

  const canBuild = !!routeFrom && !!routeTo && !isBuilding

  return (
    <div className="p-4 border-b border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Маршрут A → B</h3>
        <button
          onClick={resetRoute}
          className="text-gray-400 hover:text-gray-600 text-xs"
          title="Очистить маршрут"
        >✕</button>
      </div>

      <p className="text-xs text-gray-500 mb-3">
        {!routeFrom && 'Кликните по карте, чтобы задать точку отправления (A).'}
        {routeFrom && !routeTo && 'Кликните по карте, чтобы задать точку назначения (B).'}
        {routeFrom && routeTo && !result && 'Точки выбраны — нажмите «Построить».'}
      </p>

      <div className="flex flex-col gap-1 text-xs text-gray-600 mb-3">
        <div className="flex justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500" /> A
          </span>
          <span className="text-gray-400">
            {routeFrom ? `${routeFrom.lat.toFixed(5)}, ${routeFrom.lon.toFixed(5)}` : '—'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-red-500" /> B
          </span>
          <span className="text-gray-400">
            {routeTo ? `${routeTo.lat.toFixed(5)}, ${routeTo.lon.toFixed(5)}` : '—'}
          </span>
        </div>
      </div>

      <button
        onClick={onBuild}
        disabled={!canBuild}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium py-2 rounded-lg transition-colors"
      >
        {isBuilding ? 'Построение...' : 'Построить'}
      </button>

      {result && !result.found && (
        <p className="text-xs text-red-500 mt-3">
          Маршрут не найден: точки находятся в разных компонентах связности (вероятно, после удаления узлов).
        </p>
      )}

      {result?.found && (
        <div className="mt-3 pt-3 border-t border-gray-100 flex flex-col gap-1 text-xs text-gray-600">
          <div className="flex justify-between">
            <span>Длина маршрута</span>
            <span className="font-medium text-gray-800">{result.distance_km.toFixed(2)} км</span>
          </div>
          <div className="flex justify-between">
            <span>Время в пути</span>
            <span className="font-medium text-gray-800">≈ {Math.round(result.drive_time_minutes)} мин</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Пешком до/от перекрёстков</span>
            <span>≈ {Math.round(result.walk_time_minutes)} мин</span>
          </div>
          <div className="flex justify-between mt-1 pt-1 border-t border-gray-50">
            <span className="text-gray-700">Итого</span>
            <span className="font-semibold text-gray-900">≈ {Math.round(result.total_time_minutes)} мин</span>
          </div>
          <div className="flex justify-between text-gray-400 mt-2">
            <span>Узлов в пути</span>
            <span>{result.path.length}</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>До перекрёстка от A</span>
            <span>{(result.snap_from_distance_km * 1000).toFixed(0)} м</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>От перекрёстка до B</span>
            <span>{(result.snap_to_distance_km * 1000).toFixed(0)} м</span>
          </div>
        </div>
      )}
    </div>
  )
}
