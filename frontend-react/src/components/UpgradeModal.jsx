import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Crown, Zap, Globe, BookmarkCheck, TrendingUp, Check } from 'lucide-react'

const PLANS = [
  {
    id: 'pro',
    name: 'Pro',
    price: '$4.99',
    period: '/month',
    badge: null,
    features: [
      'Unlimited articles daily',
      'Region-based filtering',
      'Save bookmarks',
      'No ads',
    ],
    cta: 'Go Pro',
    gradient: 'from-accent to-violet',
    border: 'border-accent/40',
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '$9.99',
    period: '/month',
    badge: 'Best Value',
    features: [
      'Everything in Pro',
      'AI-powered summaries',
      'Trend analysis',
      'Daily email digest',
      'Priority support',
    ],
    cta: 'Go Premium',
    gradient: 'from-gold to-orange-500',
    border: 'border-gold/40',
  },
]

export default function UpgradeModal({ open, onClose }) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
            onClick={onClose} />
          <motion.div
            initial={{ opacity: 0, y: 80, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 60, scale: 0.95 }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-50 bg-bg-card rounded-t-3xl p-6 pb-safe border-t border-white/[0.08] max-h-[92vh] overflow-y-auto">

            {/* Handle */}
            <div className="w-10 h-1 rounded-full bg-white/20 mx-auto mb-5" />

            <button onClick={onClose}
              className="absolute top-5 right-5 p-2 rounded-full text-slate-500 hover:text-white hover:bg-white/[0.06]">
              <X size={18} />
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-gold to-orange-500 mb-4 shadow-lg">
                <Crown size={24} className="text-white" />
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Unlock Everything</h2>
              <p className="text-slate-400 text-sm">You've read your 15 free stories today.<br />Upgrade for unlimited access.</p>
            </div>

            <div className="grid grid-cols-1 gap-4 mb-6">
              {PLANS.map(plan => (
                <div key={plan.id} className={`relative rounded-2xl border p-5 ${plan.border} bg-white/[0.03]`}>
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-gold to-orange-500
                      text-black text-xs font-bold px-3 py-0.5 rounded-full shadow">
                      {plan.badge}
                    </div>
                  )}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-white font-bold">{plan.name}</h3>
                      <div className="flex items-baseline gap-1 mt-0.5">
                        <span className={`text-2xl font-bold bg-gradient-to-r ${plan.gradient} bg-clip-text text-transparent`}>
                          {plan.price}
                        </span>
                        <span className="text-slate-500 text-sm">{plan.period}</span>
                      </div>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-4">
                    {plan.features.map(f => (
                      <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                        <Check size={14} className="text-green-400 flex-shrink-0" strokeWidth={3} />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button
                    className={`w-full py-3 rounded-xl font-semibold text-sm text-white bg-gradient-to-r ${plan.gradient} active:scale-[0.98] transition-transform shadow-lg`}
                    onClick={() => alert(`Stripe integration coming soon! Plan: ${plan.name}`)}>
                    {plan.cta}
                  </button>
                </div>
              ))}
            </div>

            <p className="text-center text-slate-600 text-xs">Cancel anytime · Secure payment via Stripe</p>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
