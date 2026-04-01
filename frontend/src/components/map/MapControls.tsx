import { useGraphStore } from '../../store/graphStore'

interface Props {
  onCalculate: () => void
  onSave: () => void
}

export default function MapControls({ onCalculate, onSave }: Props) {
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const removedEdges = useGraphStore((s) => s.removedEdges)
  const resetChanges = useGraphStore((s) => s.resetChanges)
  const isCalculating = useGraphStore((s) => s.isCalculating)
  const analysisResult = useGraphStore((s) => s.analysisResult)

  const hasChanges = removedNodes.length > 0 || removedEdges.length > 0

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[1000] flex gap-3">
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

      {analysisResult && (
        <button
          onClick={onSave}
          className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg shadow text-sm font-medium transition-colors"
        >
          Сохранить
        </button>
      )}
    </div>
  )
}
