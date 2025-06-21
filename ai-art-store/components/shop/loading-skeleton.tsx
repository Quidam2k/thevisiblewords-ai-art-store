export function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Grid Loading */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm overflow-hidden">
            {/* Image skeleton */}
            <div className="aspect-square bg-gray-200 animate-pulse" />
            
            {/* Content skeleton */}
            <div className="p-4 space-y-3">
              {/* Title */}
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
              
              {/* Description */}
              <div className="h-3 bg-gray-200 rounded animate-pulse" />
              <div className="h-3 bg-gray-200 rounded w-2/3 animate-pulse" />
              
              {/* Price and category */}
              <div className="flex items-center justify-between">
                <div className="h-6 bg-gray-200 rounded w-1/3 animate-pulse" />
                <div className="h-5 bg-gray-200 rounded w-1/4 animate-pulse" />
              </div>
              
              {/* Tags */}
              <div className="flex gap-1">
                <div className="h-5 bg-gray-200 rounded w-12 animate-pulse" />
                <div className="h-5 bg-gray-200 rounded w-16 animate-pulse" />
                <div className="h-5 bg-gray-200 rounded w-14 animate-pulse" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}