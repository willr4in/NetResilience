interface Props {
  children?: React.ReactNode
  visible: boolean
}

export default function Sidebar({ children, visible }: Props) {
  return (
    <aside
      className={`
        absolute top-0 right-0 h-full w-80 z-[1000]
        bg-white/70 backdrop-blur-md border-l border-white/30
        overflow-y-auto overflow-x-hidden
        transition-transform duration-300 ease-in-out
        ${visible ? 'translate-x-0' : 'translate-x-full'}
      `}
    >
      {children}
    </aside>
  )
}
