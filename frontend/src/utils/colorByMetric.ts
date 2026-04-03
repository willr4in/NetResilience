// Возвращает цвет узла по значению betweenness (0–1)
// Низкое значение → синий, высокое → красный
export function colorByBetweenness(value: number): string {
  if (value >= 0.6) return '#ef4444' // красный — очень критичный
  if (value >= 0.4) return '#f97316' // оранжевый — критичный
  if (value >= 0.2) return '#eab308' // жёлтый — умеренный
  return '#3b82f6'                   // синий — обычный
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
  if (criticalNodes.includes(nodeId)) return colorByBetweenness(betweenness[nodeId] ?? 0)
  return '#3b82f6' // синий — обычный
}

export function nodeOpacity(nodeId: string, removedNodes: string[]): number {
  return removedNodes.includes(nodeId) ? 0.3 : 0.85
}
