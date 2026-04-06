// Возвращает цвет узла по перцентилю внутри criticalNodes
// top 33% → красный, middle 33% → оранжевый, bottom 33% → жёлтый
export function colorByRank(rank: number): string {
  if (rank >= 0.67) return '#ef4444' // красный — очень критичный
  if (rank >= 0.33) return '#f97316' // оранжевый — критичный
  return '#eab308'                   // жёлтый — умеренный
}

export function nodeColor(
  nodeId: string,
  removedNodes: string[],
  criticalNodes: string[],
  betweenness: Record<string, number>,
  isolatedNodes: string[] = []
): string {
  if (removedNodes.includes(nodeId)) return '#9ca3af' // серый — удалён
  if (isolatedNodes.includes(nodeId)) return '#a855f7' // фиолетовый — изолирован
  if (criticalNodes.includes(nodeId)) {
    const values = criticalNodes.map((id) => betweenness[id] ?? 0).sort((a, b) => a - b)
    const val = betweenness[nodeId] ?? 0
    const rank = values.length > 1 ? values.indexOf(val) / (values.length - 1) : 1
    return colorByRank(rank)
  }
  return '#3b82f6' // синий — обычный
}

export function nodeOpacity(nodeId: string, removedNodes: string[]): number {
  return removedNodes.includes(nodeId) ? 0.3 : 0.85
}
