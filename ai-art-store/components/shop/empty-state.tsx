import Link from 'next/link'
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'

interface EmptyStateProps {
  searchTerm?: string
  hasFilters?: boolean
  onClearFilters?: () => void
}

export function EmptyState({ searchTerm, hasFilters, onClearFilters }: EmptyStateProps) {
  if (searchTerm) {
    return (
      <div className="text-center py-16">
        <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No results found for "{searchTerm}"
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          We couldn't find any artwork matching your search. Try different keywords or browse our categories.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/shop"
            className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Browse All Artwork
          </Link>
          {hasFilters && onClearFilters && (
            <button
              onClick={onClearFilters}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <AdjustmentsHorizontalIcon className="h-4 w-4 mr-2" />
              Clear Filters
            </button>
          )}
        </div>
      </div>
    )
  }

  if (hasFilters) {
    return (
      <div className="text-center py-16">
        <AdjustmentsHorizontalIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No artwork matches your filters
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Try adjusting your filters or clearing them to see more results.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {onClearFilters && (
            <button
              onClick={onClearFilters}
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Clear All Filters
            </button>
          )}
          <Link
            href="/shop"
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Browse All Artwork
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="text-center py-16">
      <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-lg flex items-center justify-center">
        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        No artwork available yet
      </h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        We're working on adding beautiful AI-generated artwork to our collection. Check back soon!
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/custom"
          className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          Request Custom Art
        </Link>
        <Link
          href="/"
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back to Home
        </Link>
      </div>
    </div>
  )
}