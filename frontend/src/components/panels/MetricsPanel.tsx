import { useState } from 'react'
import type { MetricResponse } from '../../types/metrics'

type MetricKey = 'betweenness' | 'closeness' | 'degree'

interface Props {
  metrics: MetricResponse
}

const LABELS: Record<MetricKey, string> = {
  betweenness: 'Betweenness',
  closeness: 'Closeness',
  degree: 'Degree',
}

export default function MetricsPanel({ metrics }: Props) {
  const [active, setActive] = useState<MetricKey>('betweenness')

  const values = metrics[active]
  const top10 = Object.entries(values)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)

  const max = top10[0]?.[1] ?? 1

  return (
    <div className="p-4 border-b border-gray-200">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Метрики центральности</h3>

      <div className="flex gap-1 mb-3">
        {(Object.keys(LABELS) as MetricKey[]).map((key) => (
          <button
            key={key}
            onClick={() => setActive(key)}
            className={`flex-1 text-xs py-1 rounded transition-colors ${
              active === key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {LABELS[key]}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-1.5">
        {top10.map(([nodeId, value]) => (
          <div key={nodeId} className="flex items-center gap-2">
            <span className="text-xs text-gray-500 w-24 truncate">{nodeId}</span>
            <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${(value / max) * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 w-10 text-right">
              {value.toFixed(3)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
