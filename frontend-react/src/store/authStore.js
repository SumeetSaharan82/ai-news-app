import { create } from 'zustand'

const stored = (() => {
  try {
    const u = localStorage.getItem('briefed_user')
    const t = localStorage.getItem('briefed_token')
    return u && t ? { user: JSON.parse(u), token: t } : null
  } catch { return null }
})()

export const useAuthStore = create((set, get) => ({
  user:  stored?.user  ?? null,
  token: stored?.token ?? null,
  isAuthenticated: !!stored,

  setAuth({ user, access_token }) {
    localStorage.setItem('briefed_token', access_token)
    localStorage.setItem('briefed_user', JSON.stringify(user))
    set({ user, token: access_token, isAuthenticated: true })
  },

  updateUser(patch) {
    const user = { ...get().user, ...patch }
    localStorage.setItem('briefed_user', JSON.stringify(user))
    set({ user })
  },

  logout() {
    localStorage.removeItem('briefed_token')
    localStorage.removeItem('briefed_user')
    set({ user: null, token: null, isAuthenticated: false })
  },

  needsOnboarding() {
    const prefs = get().user?.preferences
    return !prefs?.categories || prefs.categories.length === 0
  },
}))
