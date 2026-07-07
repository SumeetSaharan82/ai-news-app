import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, Check, Loader2, Globe } from 'lucide-react'
import { usersApi } from '../api/users'
import { useAuthStore } from '../store/authStore'

const CATEGORIES = [
  { id: 'technology',    label: 'Technology',    emoji: '💻' },
  { id: 'business',      label: 'Business',      emoji: '📊' },
  { id: 'sports',        label: 'Sports',        emoji: '⚽' },
  { id: 'health',        label: 'Health',        emoji: '🏥' },
  { id: 'science',       label: 'Science',       emoji: '🔬' },
  { id: 'entertainment', label: 'Entertainment', emoji: '🎬' },
  { id: 'politics',      label: 'Politics',      emoji: '🏛️' },
  { id: 'world',         label: 'World',         emoji: '🌍' },
  { id: 'finance',       label: 'Finance',       emoji: '💰' },
  { id: 'general',       label: 'General',       emoji: '📰' },
]

const REGIONS = [
  { id: 'us', label: 'United States', flag: '🇺🇸' },
  { id: 'gb', label: 'United Kingdom', flag: '🇬🇧' },
  { id: 'in', label: 'India',          flag: '🇮🇳' },
  { id: 'au', label: 'Australia',      flag: '🇦🇺' },
  { id: 'ca', label: 'Canada',         flag: '🇨🇦' },
  { id: 'de', label: 'Germany',        flag: '🇩🇪' },
]

export default function OnboardingPage() {
  const [step, setStep]         = useState(0) // 0=categories, 1=regions
  const [selected, setSelected] = useState({ categories: [], regions: ['us'] })
  const [loading, setLoading]   = useState(false)
  const { updateUser } = useAuthStore()
  const navigate = useNavigate()

  function toggleCat(id) {
    setSelected(s => ({
      ...s,
      categories: s.categories.includes(id)
        ? s.categories.filter(c => c !== id)
        : [...s.categories, id]
    }))
  }

  function toggleRegion(id) {
    setSelected(s => ({
      ...s,
      regions: s.regions.includes(id)
        ? s.regions.filter(r => r !== id)
        : [...s.regions, id]
    }))
  }

  async function finish() {
    if (selected.categories.length === 0) return
    setLoading(true)
    try {
      const prefs = await usersApi.updatePreferences({
        categories: selected.categories,
        regions: selected.regions.length ? selected.regions : ['us'],
      })
      updateUser({ preferences: prefs })
      navigate('/feed', { replace: true })
    } catch {
      navigate('/feed', { replace: true })
    }
  }

  const canNext = selected.categories.length >= 1
  const canFinish = selected.regions.length >= 1

  return (
    <div className="h-screen w-screen flex flex-col bg-bg-primary overflow-hidden">
      {/* Ambient bg */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-accent/10 blur-[120px] rounded-full" />
      </div>

      {/* Progress bar */}
      <div className="relative z-10 pt-safe px-6 pt-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-500 font-medium">Step {step + 1} of 2</span>
          <span className="text-xs text-slate-500">{step === 0 ? `${selected.categories.length} selected` : `${selected.regions.length} selected`}</span>
        </div>
        <div className="h-1 w-full bg-white/[0.06] rounded-full overflow-hidden">
          <motion.div className="h-full bg-gradient-to-r from-accent to-violet rounded-full"
            animate={{ width: `${(step + 1) / 2 * 100}%` }} transition={{ duration: 0.4, ease: 'easeOut' }} />
        </div>
      </div>

      <div className="relative z-10 flex-1 flex flex-col px-6 overflow-hidden">
        <AnimatePresence mode="wait">
          {step === 0 ? (
            <motion.div key="cats" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.3 }}
              className="flex flex-col h-full">
              <div className="mt-8 mb-6">
                <h1 className="text-2xl font-bold text-white mb-2">What interests you?</h1>
                <p className="text-slate-400 text-sm">Pick at least one topic for your personalized feed.</p>
              </div>

              <div className="flex-1 overflow-y-auto pb-4">
                <div className="grid grid-cols-2 gap-3">
                  {CATEGORIES.map((cat, i) => {
                    const isSelected = selected.categories.includes(cat.id)
                    return (
                      <motion.button key={cat.id} onClick={() => toggleCat(cat.id)}
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className={`relative p-4 rounded-2xl border text-left transition-all duration-200 active:scale-95 ${
                          isSelected
                            ? 'bg-accent/15 border-accent/60 shadow-glow'
                            : 'bg-white/[0.03] border-white/[0.06] hover:border-white/20'
                        }`}>
                        <div className="text-2xl mb-2">{cat.emoji}</div>
                        <div className={`text-sm font-semibold ${isSelected ? 'text-accent-light' : 'text-slate-300'}`}>
                          {cat.label}
                        </div>
                        {isSelected && (
                          <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-accent flex items-center justify-center">
                            <Check size={12} className="text-white" strokeWidth={3} />
                          </div>
                        )}
                      </motion.button>
                    )
                  })}
                </div>
              </div>

              <div className="pb-safe pt-4">
                <button onClick={() => setStep(1)} disabled={!canNext}
                  className="btn-primary w-full flex items-center justify-center gap-2">
                  Continue <ArrowRight size={16} />
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div key="regions" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.3 }}
              className="flex flex-col h-full">
              <div className="mt-8 mb-6">
                <button onClick={() => setStep(0)} className="text-slate-500 text-sm mb-4 hover:text-slate-300 transition-colors">
                  ← Back
                </button>
                <h1 className="text-2xl font-bold text-white mb-2">Your region</h1>
                <p className="text-slate-400 text-sm">Get news relevant to where you are.</p>
              </div>

              <div className="flex-1 overflow-y-auto pb-4">
                <div className="space-y-3">
                  {REGIONS.map((r, i) => {
                    const isSelected = selected.regions.includes(r.id)
                    return (
                      <motion.button key={r.id} onClick={() => toggleRegion(r.id)}
                        initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.06 }}
                        className={`w-full flex items-center gap-4 p-4 rounded-2xl border transition-all duration-200 active:scale-[0.98] ${
                          isSelected
                            ? 'bg-accent/15 border-accent/60 shadow-glow'
                            : 'bg-white/[0.03] border-white/[0.06] hover:border-white/20'
                        }`}>
                        <span className="text-2xl">{r.flag}</span>
                        <span className={`font-medium flex-1 text-left ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                          {r.label}
                        </span>
                        {isSelected && (
                          <div className="w-5 h-5 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
                            <Check size={12} className="text-white" strokeWidth={3} />
                          </div>
                        )}
                      </motion.button>
                    )
                  })}
                </div>
              </div>

              <div className="pb-safe pt-4">
                <button onClick={finish} disabled={loading || !canFinish}
                  className="btn-primary w-full flex items-center justify-center gap-2">
                  {loading ? <Loader2 size={18} className="animate-spin" /> : (
                    <><Globe size={16} /> Start reading</>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
