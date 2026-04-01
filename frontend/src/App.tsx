import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from './constants/routes'
import ProtectedRoute from './components/common/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import MapPage from './pages/MapPage'
import ScenariosPage from './pages/ScenariosPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path={ROUTES.MAP} element={<MapPage />} />
          <Route path={ROUTES.SCENARIOS} element={<ScenariosPage />} />
          <Route path={ROUTES.HISTORY} element={<HistoryPage />} />
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.MAP} replace />} />
      </Routes>
    </BrowserRouter>
  )
}
