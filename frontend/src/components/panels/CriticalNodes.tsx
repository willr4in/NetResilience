import { useGraphStore } from '../../store/graphStore'

interface Props {
  criticalNodes: string[]
  betweenness: Record<string, number>
}

export default function CriticalNodes({ criticalNodes, betweenness }: Props) {
  const toggleNode = useGraphStore((s) => s.toggleNode)
  const removedNodes = useGraphStore((s) => s.removedNodes)
  const nodes = useGraphStore((s) => s.nodes)
  const focusOnNode = useGraphStore((s) => s.focusOnNode)

  const nodeMap = new Map(nodes.map((n) => [n.id, n]))

  const sorted = [...criticalNodes].sort(
    (a, b) => (betweenness[b] ?? 0) - (betweenness[a] ?? 0)
  )

  const handleFocus = (nodeId: string) => {
    const n = nodeMap.get(nodeId)
    if (n) focusOnNode(n.id, n.lat, n.lon)
  }

  return (
    <div className="p-4 border-b border-gray-200">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Критические узлы
        <span className="ml-2 text-xs font-normal text-gray-400">топ 20%</span>
      </h3>

      <div className="flex flex-col gap-1">
        {sorted.slice(0, 8).map((nodeId) => {
          const isRemoved = removedNodes.includes(nodeId)
          const node = nodeMap.get(nodeId)
          return (
            <div
              key={nodeId}
              className={`group flex items-center justify-between px-2 py-1 rounded text-xs cursor-pointer transition-colors ${
                isRemoved
                  ? 'bg-red-50 text-red-400 line-through'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
              onClick={() => handleFocus(nodeId)}
              title="Показать узел на карте"
            >
              <span className="truncate w-28">{node?.label ?? nodeId}</span>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">{(betweenness[nodeId] ?? 0).toFixed(4)}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); toggleNode(nodeId) }}
                  className={`text-xs opacity-0 group-hover:opacity-100 transition-opacity ${
                    isRemoved ? 'text-emerald-500 hover:text-emerald-700' : 'text-red-400 hover:text-red-600'
                  }`}
                  title={isRemoved ? 'Вернуть узел' : 'Удалить узел'}
                >
                  {isRemoved ? '↺' : '✕'}
                </button>
              </div>
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
