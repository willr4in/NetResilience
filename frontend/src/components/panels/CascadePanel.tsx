import { useGraphStore } from '../../store/graphStore'
import type { CascadeStep } from '../../types/metrics'

export default function CascadePanel() {
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const setCascadeResult = useGraphStore((s) => s.setCascadeResult)

  if (!cascadeResult) return null

  const maxScore = Math.max(
    cascadeResult.initial_resilience_score,
    ...cascadeResult.steps.map((s) => s.resilience_score)
  )

  return (
    <div className="p-4 border-t border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Каскадный отказ</h3>
        <button
          onClick={() => setCascadeResult(null)}
          className="text-gray-400 hover:text-gray-600 text-xs"
          title="Закрыть"
        >✕</button>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-2">
        <span>Начальный: {(cascadeResult.initial_resilience_score * 100).toFixed(1)}%</span>
        <span>{cascadeResult.calculation_time_ms} мс</span>
      </div>

      <div className="flex flex-col gap-1">
        {cascadeResult.steps.map((step: CascadeStep) => (
          <div key={step.step} className="flex items-center gap-2">
            <span className="text-xs text-gray-400 w-4">{step.step}</span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${(step.resilience_score / maxScore) * 100}%` }}
              />
            </div>
            <span className="text-xs w-8 text-right text-gray-600">
              {(step.resilience_score * 100).toFixed(0)}%
            </span>
            {!step.connected && (
              <span className="text-xs text-red-500" title="Граф потерял связность">✕</span>
            )}
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-400 mt-2">✕ — граф потерял связность</p>
    </div>
  )
}
