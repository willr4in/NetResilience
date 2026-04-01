import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'
import './index.css'
import App from './App.tsx'
import { useAuthStore } from './store/authStore'

const render = () =>
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )

// Используем чистый axios без interceptor чтобы избежать цикла redirect.
// При 401 пробуем refresh вручную, затем повторяем запрос.
const restoreSession = async () => {
  try {
    const { data } = await axios.get('/api/users/me', { withCredentials: true })
    useAuthStore.getState().setUser(data)
  } catch (e: any) {
    if (e?.response?.status === 401) {
      try {
        await axios.post('/api/auth/refresh', {}, { withCredentials: true })
        const { data } = await axios.get('/api/users/me', { withCredentials: true })
        useAuthStore.getState().setUser(data)
      } catch {
        // refresh тоже упал — пользователь не авторизован
      }
    }
  }
}

restoreSession().finally(render)
