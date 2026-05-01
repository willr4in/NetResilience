export default function MapSkeleton() {
  return (
    <div className="h-full w-full bg-gray-100 animate-pulse relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-gray-200 via-gray-100 to-gray-200" />
      <div className="absolute top-4 left-4 flex flex-col gap-2">
        <div className="w-8 h-8 bg-gray-300 rounded" />
        <div className="w-8 h-8 bg-gray-300 rounded" />
      </div>
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-3">
        <div className="h-9 w-24 bg-gray-300 rounded-lg" />
        <div className="h-9 w-28 bg-gray-300 rounded-lg" />
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <p className="text-sm text-gray-400 font-medium">Загрузка графа…</p>
      </div>
    </div>
  )
}
