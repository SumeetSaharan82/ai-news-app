import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { LogOut, Crown, Check, ChevronRight, Bell, Moon, Globe, User, Loader2, Edit3, X } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { usersApi } from '../api/users'
import BottomNav from '../components/BottomNav'

const CATEGORIES = [
  { id: 'technology', emoji: '💻' }, { id: 'business', emoji: '📊' },
  { id: 'sports', emoji: '⚽' },     { id: 'health', emoji: '🏥' },
  { id: 'science', emoji: '🔬' },    { id: 'entertainment', emoji: '🎬' },
  { id: 'politics', emoji: '🏛️' },   { id: 'world', emoji: '🌍' },
  { id: 'finance', emoji: '💰' },    { id: 'general', emoji: '📰' },
]
const REGIONS = [
  { id: 'us', flag: '🇺🇸', label: 'US' }, { id: 'gb', flag: '🇬🇧', label: 'UK' },
  { id: 'in', flag: '🇮🇳', label: 'India' }, { id: 'au', flag: '🇦🇺', label: 'AU' },
  { id: 'ca', flag: '🇨🇦', label: 'CA' }, { id: 'de', flag: '🇩🇪', label: 'DE' },
]

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuthStore()
  const navigate = useNavigate()

  const prefs = user?.preferences || {}
  const [selectedCats,    setSelectedCats]    = useState(prefs.categories || [])
  const [selectedRegions, setSelectedRegions] = useState(prefs.regions    || ['us'])
  const [saving,  setSaving]  = useState(false)
  const [saved,   setSaved]   = useState(false)
  const [editName, setEditName] = useState(false)
  const [nameVal,  setNameVal]  = useState(user?.name || '')
  const isPremium = prefs.tier === 'pro' || prefs.tier === 'premium'

  function toggleCat(id) {
    setSelectedCats(c => c.includes(id) ? c.filter(x => x !== id) : [...c, id])
    setSaved(false)
  }
  function toggleRegion(id) {
    setSelectedRegions(r => r.includes(id) ? r.filter(x => x !== id) : [...r, id])
    setSaved(false)
  }

  async function savePreferences() {
    if (selectedCats.length === 0) return
    setSaving(true)
    try {
      const updated = await usersApi.updatePreferences({ categories: selectedCats, regions: selectedRegions })
      updateUser({ preferences: updated })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    } catch {} finally { setSaving(false) }
  }

  async function saveName() {
    if (!nameVal.trim()) return
    try {
      await usersApi.updateProfile({ name: nameVal.trim() })
      updateUser({ name: nameVal.trim() })
      setEditName(false)
    } catch {}
  }

  const hasChanges =
    JSON.stringify(selectedCats.slice().sort()) !== JSON.stringify((prefs.categories||[]).slice().sort()) ||
    JSON.stringify(selectedRegions.slice().sort()) !== JSON.stringify((prefs.regions||[]).slice().sort())

  return (
    <div className="h-screen w-screen flex flex-col bg-bg-primary overflow-hidden">
      {/* Header */}
      <div className="pt-safe px-5 pt-8 pb-4 flex-shrink-0">
        <h1 className="text-xl font-bold text-white">Profile</h1>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto px-5 pb-28 space-y-5">

        {/* User card */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent to-violet flex items-center justify-center text-white text-xl font-bold flex-shrink-0 shadow-glow">
              {(user?.name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              {editName ? (
                <div className="flex items-center gap-2">
                  <input className="input text-sm py-2 flex-1" value={nameVal}
                    onChange={e => setNameVal(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && saveName()}
                    autoFocus />
                  <button onClick={saveName} className="text-accent"><Check size={18} /></button>
                  <button onClick={() => setEditName(false)} className="text-slate-500"><X size={16} /></button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <p className="text-white font-semibold truncate">{user?.name || 'Add your name'}</p>
                  <button onClick={() => setEditName(true)} className="text-slate-500 hover:text-slate-300">
                    <Edit3 size={13} />
                  </button>
                </div>
              )}
              <p className="text-slate-500 text-sm truncate">{user?.email}</p>
            </div>
          </div>

          {/* Plan badge */}
          <div className={`mt-4 flex items-center justify-between p-3 rounded-xl ${
            isPremium ? 'bg-gold/10 border border-gold/20' : 'bg-white/[0.04] border border-white/[0.06]'
          }`}>
            <div className="flex items-center gap-2">
              {isPremium
                ? <><Crown size={16} className="text-gold" /><span className="text-gold text-sm font-semibold">Premium Plan</span></>
                : <><User size={16} className="text-slate-400" /><span className="text-slate-400 text-sm">Free Plan · 15 articles/day</span></>
              }
            </div>
            {!isPremium && (
              <button className="text-xs font-bold text-accent hover:text-accent-light transition-colors">
                Upgrade →
              </button>
            )}
          </div>
        </motion.div>

        {/* Topics */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
          className="glass rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-1">Your Topics</h2>
          <p className="text-slate-500 text-xs mb-4">Pick at least one to personalize your feed</p>
          <div className="grid grid-cols-2 gap-2">
            {CATEGORIES.map(cat => {
              const on = selectedCats.includes(cat.id)
              return (
                <button key={cat.id} onClick={() => toggleCat(cat.id)}
                  className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm font-medium transition-all active:scale-95 ${
                    on ? 'bg-accent/15 border-accent/50 text-accent-light' : 'border-white/[0.06] text-slate-400 hover:border-white/20'
                  }`}>
                  <span>{cat.emoji}</span>
                  <span className="capitalize">{cat.id}</span>
                  {on && <Check size={12} className="ml-auto" strokeWidth={3} />}
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* Regions */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="glass rounded-2xl p-5">
          <h2 className="text-white font-semibold mb-4">Regions</h2>
          <div className="grid grid-cols-3 gap-2">
            {REGIONS.map(r => {
              const on = selectedRegions.includes(r.id)
              return (
                <button key={r.id} onClick={() => toggleRegion(r.id)}
                  className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm transition-all active:scale-95 ${
                    on ? 'bg-accent/15 border-accent/50 text-accent-light' : 'border-white/[0.06] text-slate-400 hover:border-white/20'
                  }`}>
                  <span>{r.flag}</span>
                  <span className="font-medium">{r.label}</span>
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* Save button */}
        {hasChanges && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <button onClick={savePreferences} disabled={saving || selectedCats.length === 0}
              className="btn-primary w-full flex items-center justify-center gap-2">
              {saving ? <Loader2 size={16} className="animate-spin" /> : saved ? <><Check size={16} /> Saved!</> : 'Save preferences'}
            </button>
          </motion.div>
        )}

        {/* Sign out */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <button onClick={() => { logout(); navigate('/auth', { replace: true }) }}
            className="w-full flex items-center justify-between px-4 py-3.5 rounded-2xl border border-red-500/20 bg-red-500/5 text-red-400 hover:bg-red-500/10 transition-all active:scale-[0.98]">
            <div className="flex items-center gap-3">
              <LogOut size={16} />
              <span className="text-sm font-medium">Sign out</span>
            </div>
          </button>
        </motion.div>

        <p className="text-center text-slate-700 text-xs pb-2">Briefed v1.0 · Built with ❤️</p>
      </div>

      <BottomNav />
    </div>
  )
}
