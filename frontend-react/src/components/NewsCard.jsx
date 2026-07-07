import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, ChevronDown, Share2, Bookmark, Clock, Globe, Crown } from 'lucide-react'

const CATEGORY_COLORS = {
  technology:    'text-blue-400   bg-blue-400/10   border-blue-400/20',
  business:      'text-green-400  bg-green-400/10  border-green-400/20',
  sports:        'text-orange-400 bg-orange-400/10 border-orange-400/20',
  health:        'text-pink-400   bg-pink-400/10   border-pink-400/20',
  science:       'text-cyan-400   bg-cyan-400/10   border-cyan-400/20',
  entertainment: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
  politics:      'text-red-400    bg-red-400/10    border-red-400/20',
  world:         'text-teal-400   bg-teal-400/10   border-teal-400/20',
  finance:       'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  general:       'text-slate-400  bg-slate-400/10  border-slate-400/20',
}

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 60)    return 'just now'
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function truncate(text, words = 60) {
  if (!text) return ''
  const w = text.trim().split(/\s+/)
  return w.length <= words ? text : w.slice(0, words).join(' ') + '…'
}

const FALLBACK_IMAGES = [
  'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
  'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80',
  'https://images.unsplash.com/photo-1586339949916-3e9457bef6d3?w=800&q=80',
  'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80',
  'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&q=80',
]

export default function NewsCard({ article, index, isActive, onShowUpgrade, isPremium }) {
  const [imgError, setImgError]     = useState(false)
  const [expanded, setExpanded]     = useState(false)
  const [bookmarked, setBookmarked] = useState(false)
  const [tapped, setTapped]         = useState(false)

  const fallbackImg = FALLBACK_IMAGES[index % FALLBACK_IMAGES.length]
  const imgSrc = (!imgError && article.image_url) ? article.image_url : fallbackImg

  const catColor = CATEGORY_COLORS[article.category] || CATEGORY_COLORS.general
  const summary  = truncate(article.description || article.content || article.title, 60)
  const timeStr  = article.published_at ? timeAgo(article.published_at) : ''

  async function handleShare() {
    try {
      await navigator.share({ title: article.title, url: article.url })
    } catch {
      navigator.clipboard?.writeText(article.url)
    }
  }

  function handleBookmark() {
    setBookmarked(b => !b)
    setTapped(true)
    setTimeout(() => setTapped(false), 600)
  }

  return (
    <div className="card-feed relative overflow-hidden bg-bg-primary flex flex-col">
      {/* Image */}
      <div className="relative overflow-hidden" style={{ height: '42%', flexShrink: 0 }}>
        <img
          src={imgSrc}
          alt={article.title}
          onError={() => setImgError(true)}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        {/* Gradient overlay */}
        <div className="absolute inset-0 image-gradient" />

        {/* Top badges */}
        <div className="absolute top-4 left-4 right-4 flex items-start justify-between">
          <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border uppercase tracking-wide ${catColor}`}>
            {article.category}
          </span>
          {!isPremium && index >= 10 && (
            <button onClick={onShowUpgrade}
              className="flex items-center gap-1 bg-gold/90 text-black text-[11px] font-bold px-2.5 py-1 rounded-full backdrop-blur-sm">
              <Crown size={10} /> Pro
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col px-5 pt-4 pb-2 min-h-0">
        {/* Source + time */}
        <div className="flex items-center gap-2 mb-3 flex-shrink-0">
          <Globe size={12} className="text-slate-500" />
          <span className="text-slate-400 text-xs font-medium truncate max-w-[160px]">{article.source}</span>
          {timeStr && (
            <>
              <span className="text-slate-700">·</span>
              <Clock size={11} className="text-slate-600" />
              <span className="text-slate-500 text-xs">{timeStr}</span>
            </>
          )}
        </div>

        {/* Headline */}
        <h2 className="text-white font-bold leading-snug mb-3 flex-shrink-0" style={{ fontSize: 'clamp(15px, 4vw, 20px)' }}>
          {article.title}
        </h2>

        {/* Summary */}
        <div className="flex-1 overflow-hidden">
          <p className="text-slate-400 leading-relaxed text-sm">
            {summary}
          </p>
        </div>

        {/* Actions row */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.04] flex-shrink-0 pb-safe">
          <a href={article.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 text-accent-light text-sm font-semibold hover:text-accent transition-colors active:scale-95">
            Read full story <ExternalLink size={14} />
          </a>

          <div className="flex items-center gap-1">
            <button onClick={handleShare}
              className="p-2.5 rounded-xl hover:bg-white/[0.06] text-slate-500 hover:text-slate-300 transition-all active:scale-95">
              <Share2 size={17} />
            </button>
            <motion.button onClick={handleBookmark}
              animate={tapped ? { scale: [1, 1.3, 1] } : {}}
              className={`p-2.5 rounded-xl hover:bg-white/[0.06] transition-all active:scale-95 ${
                bookmarked ? 'text-accent' : 'text-slate-500 hover:text-slate-300'
              }`}>
              <Bookmark size={17} fill={bookmarked ? 'currentColor' : 'none'} />
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  )
}
