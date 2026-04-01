import { useGraphStore } from '../../store/graphStore'

interface Props {
  criticalNodes: string[]
  betweenness: Record<string, number>
}

export default function CriticalNodes({ criticalNodes, betweenness }: Props) {
  const toggleNode = useGraphStore((s) => s.toggleNode)
  const removedNodes = useGraphStore((s) => s.removedNodes)

  const sorted = [...criticalNodes].sort(
    (a, b) => (betweenness[b] ?? 0) - (betweenness[a] ?? 0)
  )

  return (
    <div className="p-4 border-b border-gray-200">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Критические узлы
        <span className="ml-2 text-xs font-normal text-gray-400">топ 20%</span>
      </h3>

      <div className="flex flex-col gap-1">
        {sorted.slice(0, 8).map((nodeId) => {
          const isRemoved = removedNodes.includes(nodeId)
          return (
            <div
              key={nodeId}
              className={`flex items-center justify-between px-2 py-1 rounded text-xs cursor-pointer transition-colors ${
                isRemoved
                  ? 'bg-red-50 text-red-400 line-through'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
              onClick={() => toggleNode(nodeId)}
            >
              <span className="truncate w-32">{nodeId}</span>
              <span className="text-gray-400">{(betweenness[nodeId] ?? 0).toFixed(4)}</span>
            </div>
          )
        })}
      </div>

      {criticalNodes.length > 8 && (
        <p className="text-xs text-gray-400 mt-2">
          +{criticalNodes.length - 8} узлов
        </p>
      )}
    </div>
  )
}
