import { NavLink, useNavigate } from 'react-router-dom'
import { ROUTES } from '../../constants/routes'
import { useAuthStore } from '../../store/authStore'
import { logout } from '../../api/auth'

export default function Header() {
  const clearUser = useAuthStore((s) => s.clearUser)
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    clearUser()
    navigate(ROUTES.LOGIN)
  }

  return (
    <header className="h-14 bg-gray-900 text-white flex items-center justify-between px-6 shrink-0">
      <span className="font-semibold text-lg tracking-wide">NetResilience</span>

      <nav className="flex gap-6 text-sm">
        <NavLink
          to={ROUTES.MAP}
          className={({ isActive }) => isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}
        >
          Карта
        </NavLink>
        <NavLink
          to={ROUTES.SCENARIOS}
          className={({ isActive }) => isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}
        >
          Сценарии
        </NavLink>
        <NavLink
          to={ROUTES.HISTORY}
          className={({ isActive }) => isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}
        >
          История
        </NavLink>
        <NavLink
          to={ROUTES.HELP}
          className={({ isActive }) => isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}
        >
          Справка
        </NavLink>
      </nav>

      <button
        onClick={handleLogout}
        className="text-sm text-gray-400 hover:text-white transition-colors"
      >
        Выйти
      </button>
    </header>
  )
}
