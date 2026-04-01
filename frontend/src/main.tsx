import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { getMe } from './api/auth'
import { useAuthStore } from './store/authStore'

getMe()
  .then(({ data }) => useAuthStore.getState().setUser(data))
  .catch(() => {})
  .finally(() => {
    createRoot(document.getElementById('root')!).render(
      <StrictMode>
        <App />
      </StrictMode>,
    )
  })
