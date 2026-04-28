import type { ResilienceMetrics } from '../../types/metrics'
import { useGraphStore } from '../../store/graphStore'

interface Props {
  resilience: ResilienceMetrics
}

function ScoreBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-semibold w-10 text-right">{pct}%</span>
    </div>
  )
}

export default function ResiliencePanel({ resilience }: Props) {
  const { resilience_score, connected, largest_component_ratio, betweenness_concentration, comparison } = resilience
  const setAnalysisResult = useGraphStore((s) => s.setAnalysisResult)

  return (
    <div className="p-4 border-b border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Устойчивость сети</h3>
        <button
          onClick={() => setAnalysisResult(null)}
          className="text-gray-400 hover:text-gray-600 text-xs"
          title="Закрыть"
        >✕</button>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Resilience Score</span>
          {comparison && (
            <span className={comparison.resilience_delta >= 0 ? 'text-green-600' : 'text-red-500'}>
              {comparison.resilience_delta >= 0 ? '+' : ''}{(comparison.resilience_delta * 100).toFixed(1)}%
            </span>
          )}
        </div>
        <ScoreBar value={resilience_score} />
      </div>

      <div className="flex flex-col gap-1 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>Граф связен</span>
          <span className={connected ? 'text-green-600 font-medium' : 'text-red-500 font-medium'}>
            {connected ? 'Да' : 'Нет'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Крупнейшая компонента</span>
          <span className="font-medium">{(largest_component_ratio * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span>Концентрация нагрузки</span>
          <span className="font-medium">{(betweenness_concentration * 100).toFixed(1)}%</span>
        </div>
      </div>

      {comparison && (
        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
          <div className="flex justify-between">
            <span>До изменений</span>
            <span>{(comparison.resilience_score_before * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span>После изменений</span>
            <span>{(comparison.resilience_score_after * 100).toFixed(1)}%</span>
          </div>
        </div>
      )}
    </div>
  )
}
