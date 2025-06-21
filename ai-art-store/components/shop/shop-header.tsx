'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'
import { debounce } from '@/lib/utils'

interface ShopHeaderProps {
  searchTerm: string
  onSearch: (term: string) => void
  sortBy: string
  onSort: (sortBy: string) => void
  resultCount: number
  filtersOpen: boolean
  onToggleFilters: () => void
}

export function ShopHeader({
  searchTerm,
  onSearch,
  sortBy,
  onSort,
  resultCount,
  filtersOpen,
  onToggleFilters,
}: ShopHeaderProps) {
  const [localSearch, setLocalSearch] = useState(searchTerm)
  const debouncedSearch = useRef(debounce(onSearch, 300))

  useEffect(() => {
    setLocalSearch(searchTerm)
  }, [searchTerm])

  useEffect(() => {
    debouncedSearch.current(localSearch)
  }, [localSearch])

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'price-low', label: 'Price: Low to High' },
    { value: 'price-high', label: 'Price: High to Low' },
    { value: 'popular', label: 'Most Popular' },
  ]

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumbs */}
        <nav className="py-4 text-sm">
          <ol className="flex items-center space-x-2 text-gray-500">
            <li>
              <Link href="/" className="hover:text-gray-700 transition-colors">
                Home
              </Link>
            </li>
            <li>
              <span className="mx-2">/</span>
            </li>
            <li className="text-gray-900 font-medium">Shop</li>
          </ol>
        </nav>

        {/* Main Header */}
        <div className="py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            {/* Title and Results Count */}
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI Art Collection
              </h1>
              <p className="text-gray-600 mt-1">
                {resultCount > 0 ? (
                  <>Showing {resultCount} unique artwork{resultCount !== 1 ? 's' : ''}</>
                ) : (
                  'Explore our collection of AI-generated art'
                )}
              </p>
            </div>

            {/* Search and Sort Controls */}
            <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
              {/* Search Bar */}
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search artwork..."
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                  className="pl-10 pr-4 py-2 w-full sm:w-64 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Sort Dropdown */}
              <select
                value={sortBy}
                onChange={(e) => onSort(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              {/* Mobile Filter Toggle */}
              <button
                onClick={onToggleFilters}
                className="lg:hidden flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <AdjustmentsHorizontalIcon className="h-5 w-5" />
                Filters
                {filtersOpen && (
                  <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded-full">
                    Open
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}