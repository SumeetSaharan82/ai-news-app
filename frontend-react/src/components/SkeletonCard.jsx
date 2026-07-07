import React from 'react'

export default function SkeletonCard() {
  return (
    <div className="card-feed flex flex-col bg-bg-primary relative overflow-hidden">
      {/* Image skeleton */}
      <div className="w-full shimmer-bg" style={{ height: '45%' }} />

      {/* Content skeleton */}
      <div className="flex-1 px-5 py-5 flex flex-col gap-4">
        {/* Category badge */}
        <div className="w-20 h-5 rounded-full shimmer-bg" />

        {/* Title */}
        <div className="space-y-2.5">
          <div className="h-5 rounded-xl shimmer-bg w-full" />
          <div className="h-5 rounded-xl shimmer-bg w-5/6" />
          <div className="h-5 rounded-xl shimmer-bg w-4/6" />
        </div>

        {/* Summary lines */}
        <div className="space-y-2 mt-1">
          <div className="h-3.5 rounded-lg shimmer-bg w-full" />
          <div className="h-3.5 rounded-lg shimmer-bg w-full" />
          <div className="h-3.5 rounded-lg shimmer-bg w-3/4" />
        </div>

        {/* Meta */}
        <div className="flex gap-3 mt-auto">
          <div className="h-3 rounded-lg shimmer-bg w-20" />
          <div className="h-3 rounded-lg shimmer-bg w-16" />
        </div>
      </div>
    </div>
  )
}
