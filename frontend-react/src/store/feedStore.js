import { create } from 'zustand'

export const useFeedStore = create((set, get) => ({
  articles:    [],
  isLoading:   false,
  error:       null,
  currentIdx:  0,
  hasMore:     true,
  filter:      { category: null, region: null, search: '' },

  setArticles(articles) { set({ articles, currentIdx: 0 }) },
  appendArticles(more)  { set(s => ({ articles: [...s.articles, ...more] })) },
  setLoading(v)         { set({ isLoading: v }) },
  setError(e)           { set({ error: e }) },
  setCurrentIdx(i)      { set({ currentIdx: i }) },
  setFilter(f)          { set(s => ({ filter: { ...s.filter, ...f }, currentIdx: 0 })) },

  // Free plan daily limit
  FREE_LIMIT: 15,
  savedCount: (() => {
    try { return parseInt(localStorage.getItem('briefed_daily_count') || '0', 10) } catch { return 0 }
  })(),
  lastReset: (() => {
    try { return localStorage.getItem('briefed_last_reset') || '' } catch { return '' }
  })(),

  checkAndIncrementCount() {
    const today = new Date().toDateString()
    const { lastReset, savedCount } = get()
    let count = savedCount
    if (lastReset !== today) {
      count = 0
      localStorage.setItem('briefed_last_reset', today)
    }
    count++
    localStorage.setItem('briefed_daily_count', String(count))
    set({ savedCount: count, lastReset: today })
    return count
  },

  isOverLimit(isPremium) {
    if (isPremium) return false
    const today = new Date().toDateString()
    const { lastReset, savedCount, FREE_LIMIT } = get()
    if (lastReset !== today) return false
    return savedCount >= FREE_LIMIT
  },
}))
