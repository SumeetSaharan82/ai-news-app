import React, { useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import AuthPage from './pages/AuthPage'
import OnboardingPage from './pages/OnboardingPage'
import FeedPage from './pages/FeedPage'
import ProfilePage from './pages/ProfilePage'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/auth" replace />
  return children
}

function OnboardingGuard({ children }) {
  const { isAuthenticated, needsOnboarding } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/auth" replace />
  if (needsOnboarding()) return <Navigate to="/onboarding" replace />
  return children
}

export default function App() {
  const { logout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    const handler = () => { logout(); navigate('/auth') }
    window.addEventListener('auth:logout', handler)
    return () => window.removeEventListener('auth:logout', handler)
  }, [logout, navigate])

  return (
    <Routes>
      <Route path="/auth" element={
        isAuthenticated ? <Navigate to="/feed" replace /> : <AuthPage />
      } />
      <Route path="/onboarding" element={
        <ProtectedRoute><OnboardingPage /></ProtectedRoute>
      } />
      <Route path="/feed" element={
        <OnboardingGuard><FeedPage /></OnboardingGuard>
      } />
      <Route path="/profile" element={
        <OnboardingGuard><ProfilePage /></OnboardingGuard>
      } />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/feed' : '/auth'} replace />} />
    </Routes>
  )
}
