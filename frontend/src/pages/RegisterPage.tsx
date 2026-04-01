import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register, login, getMe } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { ROUTES } from '../constants/routes'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const setUser = useAuthStore((s) => s.setUser)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await register({ name, surname, email, password })
      await login({ email, password })
      const { data: user } = await getMe()
      setUser(user)
      navigate(ROUTES.MAP)
    } catch {
      setError('Ошибка регистрации. Возможно, email уже занят.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-md p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold text-gray-800 mb-6">Регистрация</h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-sm text-gray-600 mb-1">Имя</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-600 mb-1">Фамилия</label>
              <input
                type="text"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            {isLoading ? 'Регистрация...' : 'Создать аккаунт'}
          </button>
        </form>

        <p className="text-sm text-gray-500 mt-4 text-center">
          Уже есть аккаунт?{' '}
          <Link to={ROUTES.LOGIN} className="text-blue-600 hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
