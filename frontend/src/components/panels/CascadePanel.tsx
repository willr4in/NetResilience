import { useGraphStore } from '../../store/graphStore'
import type { CascadeStep } from '../../types/metrics'

export default function CascadePanel() {
  const cascadeResult = useGraphStore((s) => s.cascadeResult)
  const setCascadeResult = useGraphStore((s) => s.setCascadeResult)
  const nodes = useGraphStore((s) => s.nodes)
  const focusOnNode = useGraphStore((s) => s.focusOnNode)
  const applyCascadeToScenario = useGraphStore((s) => s.applyCascadeToScenario)

  if (!cascadeResult) return null

  const nodeMap = new Map(nodes.map((n) => [n.id, n]))
  const handleStepClick = (nodeId: string) => {
    const n = nodeMap.get(nodeId)
    if (n) focusOnNode(n.id, n.lat, n.lon)
  }

  const finalScore = cascadeResult.steps.length
    ? cascadeResult.steps[cascadeResult.steps.length - 1].resilience_score
    : cascadeResult.initial_resilience_score
  const delta = finalScore - cascadeResult.initial_resilience_score

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

      <div className="flex justify-between items-baseline mb-3 px-2 py-2 bg-gray-50 rounded">
        <span className="text-xs text-gray-500">Итоговый</span>
        <div className="flex items-baseline gap-2">
          <span className="text-base font-semibold text-gray-800">
            {(finalScore * 100).toFixed(1)}%
          </span>
          <span className={`text-xs font-medium ${delta < 0 ? 'text-red-500' : delta > 0 ? 'text-green-600' : 'text-gray-400'}`}>
            {delta >= 0 ? '+' : ''}{(delta * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        {cascadeResult.steps.map((step: CascadeStep) => (
          <div
            key={step.step}
            className="flex items-center gap-2 px-1 py-0.5 rounded cursor-pointer hover:bg-gray-100 transition-colors"
            onClick={() => handleStepClick(step.removed_node_id)}
            title={`Показать ${step.removed_node_label} на карте`}
          >
            <span className="text-xs text-gray-400 w-4">{step.step}</span>
            <span className="text-xs text-gray-500 truncate w-20">{step.removed_node_label}</span>
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

      <button
        onClick={applyCascadeToScenario}
        className="mt-3 w-full text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg py-2 transition-colors"
        title="Перенести каскадно удалённые узлы в текущий сценарий, чтобы пересчитать метрики и увидеть посткаскадное состояние"
      >
        Применить к сценарию
      </button>
      <p className="text-xs text-gray-400 mt-1">
        После применения нажмите «Рассчитать», чтобы получить полные метрики посткаскадной сети.
      </p>
    </div>
  )
}
