interface Props {
  children?: React.ReactNode
}

export default function Sidebar({ children }: Props) {
  return (
    <aside className="w-80 shrink-0 bg-gray-50 border-l border-gray-200 overflow-y-auto">
      {children}
    </aside>
  )
}
