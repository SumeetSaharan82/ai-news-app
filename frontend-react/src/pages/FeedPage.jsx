import React, { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X, RefreshCw, Wifi, WifiOff, ChevronUp, ChevronDown, Crown } from 'lucide-react'
import { newsApi } from '../api/news'
import { usageApi } from '../api/usage'
import { useAuthStore } from '../store/authStore'
import { useFeedStore } from '../store/feedStore'
import NewsCard from '../components/NewsCard'
import SkeletonCard from '../components/SkeletonCard'
import UpgradeModal from '../components/UpgradeModal'
import BottomNav from '../components/BottomNav'

const CATEGORY_EMOJIS = {
  technology: '💻', business: '📊', sports: '⚽', health: '🏥',
  science: '🔬', entertainment: '🎬', politics: '🏛️', world: '🌍',
  finance: '💰', general: '📰',
}

export default function FeedPage() {
  const { user } = useAuthStore()
  const { articles, isLoading, error, currentIdx, filter, setArticles, setLoading,
          setError, setCurrentIdx, setFilter, isOverLimit, checkAndIncrementCount } = useFeedStore()

  const [showSearch, setShowSearch]     = useState(false)
  const [searchInput, setSearchInput]   = useState('')
  const [showUpgrade, setShowUpgrade]   = useState(false)
  const [refreshing, setRefreshing]     = useState(false)
  const [online, setOnline]             = useState(navigator.onLine)
  const [usageStatus, setUsageStatus]   = useState(null)
  const containerRef   = useRef(null)
  const fetchedRef     = useRef(false)
  const seenArticles   = useRef(new Set())
  // Keep a ref to current articles to avoid stale closure in scroll handler
  const articlesRef    = useRef(articles)

  const prefs      = user?.preferences || {}
  const isPremium  = prefs.tier === 'pro' || prefs.tier === 'premium'
  const categories = prefs.categories || []

  // Online status
  useEffect(() => {
    const up   = () => setOnline(true)
    const down = () => setOnline(false)
    window.addEventListener('online', up)
    window.addEventListener('offline', down)
    return () => { window.removeEventListener('online', up); window.removeEventListener('offline', down) }
  }, [])

  const fetchFeed = useCallback(async (opts = {}) => {
    setLoading(true)
    setError(null)
    try {
      // Try personalized first, fall back to RSS
      let arts = []
      try {
        const res = await newsApi.getPersonalized({ limit: 40 })
        arts = res.articles || []
      } catch {
        const res = await newsApi.getRss({
          category: filter.category || (categories[0] || undefined),
          limit: 30,
        })
        arts = res.articles || []
      }

      if (filter.search) {
        const q = filter.search.toLowerCase()
        arts = arts.filter(a =>
          a.title?.toLowerCase().includes(q) ||
          a.description?.toLowerCase().includes(q)
        )
      }
      if (filter.category) {
        arts = arts.filter(a => a.category === filter.category)
      }

      setArticles(arts)
    } catch (e) {
      setError('Failed to load news. Check your connection.')
    } finally {
      setLoading(false)
    }
  }, [filter.category, filter.search, categories.join(',')])

  useEffect(() => {
    if (!fetchedRef.current || refreshing) {
      fetchedRef.current = true
      fetchFeed()
      setRefreshing(false)
    }
  }, [fetchFeed, refreshing])

  // Fetch server-side usage status on mount
  useEffect(() => {
    usageApi.getStatus().then(setUsageStatus).catch(() => {})
  }, [])

  // Keep articlesRef in sync so the scroll handler never reads stale state
  useEffect(() => { articlesRef.current = articles }, [articles])

  // Sync currentIdx on scroll — uses articlesRef to avoid stale closure over articles
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const isPremiumRef = { current: isPremium }
    const handler = async () => {
      const idx = Math.round(el.scrollTop / el.clientHeight)
      setCurrentIdx(idx)
      // Record server-side read only for new unique articles
      const article = articlesRef.current[idx]
      const articleId = article?.id || article?.url
      if (articleId && !seenArticles.current.has(articleId)) {
        seenArticles.current.add(articleId)
        if (!isPremiumRef.current) {
          const result = await usageApi.recordRead()
          if (result.limitExceeded) {
            setShowUpgrade(true)
          } else if (result.data) {
            setUsageStatus(s => s ? { ...s, reads_today: result.data.reads_today, remaining: result.data.remaining } : s)
          }
        }
      }
    }
    el.addEventListener('scroll', handler, { passive: true })
    return () => el.removeEventListener('scroll', handler)
  // Re-register only when isPremium changes; articles always read from ref
  }, [isPremium])

  // Arrow key navigation
  useEffect(() => {
    const handler = (e) => {
      if (!containerRef.current) return
      const el = containerRef.current
      if (e.key === 'ArrowDown' || e.key === 'j') {
        el.scrollTo({ top: (currentIdx + 1) * el.clientHeight, behavior: 'smooth' })
      }
      if (e.key === 'ArrowUp' || e.key === 'k') {
        el.scrollTo({ top: Math.max(0, (currentIdx - 1)) * el.clientHeight, behavior: 'smooth' })
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [currentIdx])

  function handleCategoryFilter(cat) {
    fetchedRef.current = false
    setFilter({ category: filter.category === cat ? null : cat })
  }

  function handleSearch(e) {
    e.preventDefault()
    fetchedRef.current = false
    setFilter({ search: searchInput })
    setShowSearch(false)
  }

  function handleRefresh() {
    fetchedRef.current = false
    setRefreshing(true)
  }

  function scrollTo(idx) {
    containerRef.current?.scrollTo({ top: idx * containerRef.current.clientHeight, behavior: 'smooth' })
  }

  const progress = articles.length > 1
    ? Math.min(100, ((currentIdx + 1) / articles.length) * 100) : 0

  return (
    <div className="h-screen w-screen flex flex-col bg-bg-primary overflow-hidden relative">
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-30 pt-safe">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center shadow-glow flex-shrink-0">
              <span className="text-white text-xs font-bold">B</span>
            </div>
            <span className="text-white font-bold text-sm tracking-tight">Briefed</span>
            {!online && <WifiOff size={14} className="text-red-400 ml-1" />}
          </div>

          <div className="flex items-center gap-1">
            {!isPremium && (
              <button onClick={() => setShowUpgrade(true)}
                className="flex items-center gap-1 text-[11px] font-bold text-gold border border-gold/30 px-2.5 py-1 rounded-full bg-gold/10 hover:bg-gold/20 transition-colors">
                <Crown size={10} /> Upgrade
              </button>
            )}
            <button onClick={() => setShowSearch(s => !s)}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.06] transition-all active:scale-95">
              {showSearch ? <X size={18} /> : <Search size={18} />}
            </button>
            <button onClick={handleRefresh}
              className={`p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.06] transition-all active:scale-95 ${isLoading ? 'animate-spin text-accent' : ''}`}>
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

        {/* Search bar */}
        <AnimatePresence>
          {showSearch && (
            <motion.form onSubmit={handleSearch}
              initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}
              className="px-4 pb-3">
              <input className="input text-sm" placeholder="Search news…"
                value={searchInput} onChange={e => setSearchInput(e.target.value)}
                autoFocus />
            </motion.form>
          )}
        </AnimatePresence>

        {/* Category filter chips */}
        {categories.length > 0 && (
          <div className="px-4 pb-2 flex gap-2 overflow-x-auto" style={{ scrollbarWidth: 'none' }}>
            {categories.map(cat => (
              <button key={cat} onClick={() => handleCategoryFilter(cat)}
                className={`flex-shrink-0 flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-full border transition-all active:scale-95 ${
                  filter.category === cat
                    ? 'bg-accent/20 border-accent/60 text-accent-light'
                    : 'bg-white/[0.04] border-white/[0.08] text-slate-400 hover:border-white/20'
                }`}>
                <span>{CATEGORY_EMOJIS[cat]}</span>
                <span>{cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
              </button>
            ))}
          </div>
        )}

        {/* Progress bar */}
        {articles.length > 0 && (
          <div className="h-0.5 bg-white/[0.04] mx-4 rounded-full overflow-hidden">
            <motion.div className="h-full bg-accent/60 rounded-full"
              animate={{ width: `${progress}%` }} transition={{ duration: 0.3 }} />
          </div>
        )}
      </div>

      {/* Feed */}
      {isLoading && articles.length === 0 ? (
        <div ref={containerRef} className="feed-container pt-[120px]">
          {[0,1,2].map(i => <SkeletonCard key={i} />)}
        </div>
      ) : error && articles.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-8">
          <div className="text-4xl">📡</div>
          <p className="text-slate-400 text-sm">{error}</p>
          <button onClick={handleRefresh} className="btn-primary">Try again</button>
        </div>
      ) : articles.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-8">
          <div className="text-4xl">🔍</div>
          <p className="text-white font-semibold">No articles found</p>
          <p className="text-slate-500 text-sm">Try a different filter or refresh.</p>
          <button onClick={handleRefresh} className="btn-primary">Refresh</button>
        </div>
      ) : (
        <div ref={containerRef} className="feed-container pt-[110px]" style={{ paddingBottom: '72px' }}>
          {articles.map((article, idx) => (
            <NewsCard
              key={article.id || article.url || idx}
              article={article}
              index={idx}
              isActive={idx === currentIdx}
              isPremium={isPremium}
              onShowUpgrade={() => setShowUpgrade(true)}
            />
          ))}
          {/* End card */}
          <div className="card-feed flex flex-col items-center justify-center gap-4 text-center px-8">
            <div className="text-5xl">✨</div>
            <h3 className="text-white font-bold text-lg">You're all caught up!</h3>
            <p className="text-slate-400 text-sm">Check back later for more news.</p>
            <button onClick={handleRefresh} className="btn-primary">Refresh feed</button>
          </div>
        </div>
      )}

      {/* Nav arrows (desktop) */}
      {articles.length > 0 && (
        <div className="hidden lg:flex absolute right-6 top-1/2 -translate-y-1/2 z-30 flex-col gap-2">
          <button onClick={() => scrollTo(Math.max(0, currentIdx - 1))}
            disabled={currentIdx === 0}
            className="p-3 glass rounded-2xl text-slate-400 hover:text-white disabled:opacity-20 transition-all active:scale-95">
            <ChevronUp size={20} />
          </button>
          <div className="text-center text-xs text-slate-600 py-1">
            {currentIdx + 1}/{articles.length}
          </div>
          <button onClick={() => scrollTo(Math.min(articles.length, currentIdx + 1))}
            className="p-3 glass rounded-2xl text-slate-400 hover:text-white transition-all active:scale-95">
            <ChevronDown size={20} />
          </button>
        </div>
      )}

      <BottomNav />
      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} />
    </div>
  )
}
