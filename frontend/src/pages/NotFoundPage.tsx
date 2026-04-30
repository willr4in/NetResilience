import { Link } from 'react-router-dom'
import { ROUTES } from '../constants/routes'
import { useAuthStore } from '../store/authStore'

export default function NotFoundPage() {
  const user = useAuthStore((s) => s.user)
  const target = user ? ROUTES.MAP : ROUTES.LOGIN
  const targetLabel = user ? 'Вернуться на карту' : 'Войти'

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-6">
      <div className="bg-white rounded-xl shadow-md p-10 w-full max-w-md text-center">
        <h1 className="text-6xl font-semibold text-gray-300">404</h1>
        <h2 className="text-lg font-semibold text-gray-800 mt-4">Страница не найдена</h2>
        <p className="text-sm text-gray-500 mt-2">
          Запрошенный адрес не существует. Возможно, ссылка устарела или была введена с ошибкой.
        </p>
        <Link
          to={target}
          className="inline-block mt-6 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
        >
          {targetLabel}
        </Link>
      </div>
    </div>
  )
}
