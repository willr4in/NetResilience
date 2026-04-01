import { useState } from 'react'
import { useGraphStore } from '../../store/graphStore'
import { simulateCascade } from '../../api/graph'
import { DISTRICT } from '../../constants/map'
import type { CascadeStep } from '../../types/metrics'

export default function CascadePanel() {
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const setCascadeResult = useGraphStore((s) => s.setCascadeResult)
  const [isLoading, setIsLoading] = useState(false)
  const [steps, setSteps] = useState(10)

  const handleSimulate = async () => {
    setIsLoading(true)
    try {
      const { data } = await simulateCascade({ district: DISTRICT, steps })
      setCascadeResult(data)
    } finally {
      setIsLoading(false)
    }
  }

  const maxScore = cascadeResult
    ? Math.max(cascadeResult.initial_resilience_score, ...cascadeResult.steps.map((s) => s.resilience_score))
    : 1

  return (
    <div className="p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Каскадный отказ</h3>

      <div className="flex items-center gap-2 mb-3">
        <label className="text-xs text-gray-500">Шагов:</label>
        <input
          type="number"
          min={1}
          max={20}
          value={steps}
          onChange={(e) => setSteps(Number(e.target.value))}
          className="w-16 border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <button
          onClick={handleSimulate}
          disabled={isLoading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded py-1 text-xs font-medium transition-colors"
        >
          {isLoading ? 'Симуляция...' : 'Запустить'}
        </button>
      </div>

      {cascadeResult && (
        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-2">
            <span>Начальный score: {(cascadeResult.initial_resilience_score * 100).toFixed(1)}%</span>
            <span>{cascadeResult.calculation_time_ms}мс</span>
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
                  <span className="text-xs text-red-500">✕</span>
                )}
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-400 mt-2">
            ✕ — граф потерял связность
          </p>
        </div>
      )}
    </div>
  )
}
