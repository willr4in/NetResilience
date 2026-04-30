import { useState } from 'react'
import { useGraphStore } from '../../store/graphStore'

interface Props {
  onCalculate: () => void
  onCascade: (steps: number) => void
  onSave: () => void
}

export default function MapControls({ onCalculate, onCascade, onSave }: Props) {
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const addedNodes = useGraphStore((s) => s.addedNodes)
  const addedEdges = useGraphStore((s) => s.addedEdges)
  const resetChanges = useGraphStore((s) => s.resetChanges)
  const isCalculating = useGraphStore((s) => s.isCalculating)
  const analysisResult = useGraphStore((s) => s.analysisResult)
  const isDirty = useGraphStore((s) => s.isDirty)
  const [steps, setSteps] = useState(10)

  const hasChanges =
    removedNodes.length > 0 ||
    removedEdges.length > 0 ||
    addedNodes.length > 0 ||
    addedEdges.length > 0

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-3">
      {hasChanges && (
        <button
          onClick={resetChanges}
          className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg shadow text-sm hover:bg-gray-50 transition-colors"
        >
          Сбросить
        </button>
      )}

      <button
        onClick={onCalculate}
        disabled={isCalculating}
        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2 rounded-lg shadow text-sm font-medium transition-colors"
      >
        {isCalculating ? 'Расчёт...' : 'Рассчитать'}
      </button>

      <div className="flex items-center bg-white border border-gray-300 rounded-lg shadow overflow-hidden">
        <button
          onClick={() => onCascade(steps)}
          disabled={isCalculating}
          title="Симуляция каскадного отказа"
          className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          Каскад
        </button>
        <div className="w-px h-6 bg-gray-200" />
        <input
          type="number"
          min={1}
          max={20}
          value={steps}
          onChange={(e) => setSteps(Number(e.target.value))}
          title="Количество шагов симуляции"
          className="w-12 text-center text-xs text-gray-600 py-2 focus:outline-none"
        />
      </div>

      {analysisResult && !isDirty && (
        <>
          <button
            onClick={onSave}
            className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg shadow text-sm font-medium transition-colors"
          >
            Сохранить
          </button>
        </>
      )}
    </div>
  )
}
