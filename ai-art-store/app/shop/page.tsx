'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { ShopHeader } from '@/components/shop/shop-header'
import { ShopFilters } from '@/components/shop/shop-filters'
import { ProductGrid } from '@/components/shop/product-grid'
import { LoadingSkeleton } from '@/components/shop/loading-skeleton'
import { EmptyState } from '@/components/shop/empty-state'
import { ProductWithArtwork, ProductFilters } from '@/types'

interface ShopPageData {
  products: ProductWithArtwork[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
  filters: ProductFilters
}

export default function ShopPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  
  const [data, setData] = useState<ShopPageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filtersOpen, setFiltersOpen] = useState(false)

  // Extract current filters from URL
  const currentFilters: ProductFilters = {
    page: parseInt(searchParams.get('page') || '1'),
    limit: parseInt(searchParams.get('limit') || '12'),
    category: searchParams.get('category') || undefined,
    style: searchParams.get('style') as any || undefined,
    search: searchParams.get('search') || undefined,
    sortBy: searchParams.get('sortBy') as any || 'newest',
    priceRange: {
      min: searchParams.get('minPrice') ? parseInt(searchParams.get('minPrice')!) : undefined,
      max: searchParams.get('maxPrice') ? parseInt(searchParams.get('maxPrice')!) : undefined,
    },
    tags: searchParams.getAll('tags'),
  }

  // Fetch products based on current filters with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchProducts()
    }, 300) // Debounce API calls

    return () => clearTimeout(timeoutId)
  }, [searchParams])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      setError(null)

      // Build query string from current filters
      const queryParams = new URLSearchParams()
      
      Object.entries(currentFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (key === 'priceRange') {
            if (value.min) queryParams.set('minPrice', value.min.toString())
            if (value.max) queryParams.set('maxPrice', value.max.toString())
          } else if (key === 'tags' && Array.isArray(value)) {
            value.forEach(tag => queryParams.append('tags', tag))
          } else {
            queryParams.set(key, value.toString())
          }
        }
      })

      const response = await fetch(`/api/products?${queryParams.toString()}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch products')
      }

      const result = await response.json()
      setData(result)

    } catch (err) {
      console.error('Error fetching products:', err)
      setError('Failed to load products. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const updateFilters = (newFilters: Partial<ProductFilters>) => {
    const params = new URLSearchParams(searchParams.toString())
    
    // Update URL parameters
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        params.delete(key)
        if (key === 'priceRange') {
          params.delete('minPrice')
          params.delete('maxPrice')
        }
      } else if (key === 'priceRange' && typeof value === 'object') {
        if (value.min) params.set('minPrice', value.min.toString())
        else params.delete('minPrice')
        if (value.max) params.set('maxPrice', value.max.toString())
        else params.delete('maxPrice')
      } else if (key === 'tags' && Array.isArray(value)) {
        params.delete('tags')
        value.forEach(tag => params.append('tags', tag))
      } else {
        params.set(key, value.toString())
      }
    })

    // Reset to page 1 when filters change (except for page changes)
    if (!('page' in newFilters)) {
      params.set('page', '1')
    }

    router.push(`/shop?${params.toString()}`)
  }

  const handleSearch = (searchTerm: string) => {
    updateFilters({ search: searchTerm })
  }

  const handleSort = (sortBy: string) => {
    updateFilters({ sortBy: sortBy as any })
  }

  const handlePageChange = (page: number) => {
    updateFilters({ page })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <ShopHeader
        searchTerm={currentFilters.search || ''}
        onSearch={handleSearch}
        sortBy={currentFilters.sortBy || 'newest'}
        onSort={handleSort}
        resultCount={data?.pagination.total || 0}
        filtersOpen={filtersOpen}
        onToggleFilters={() => setFiltersOpen(!filtersOpen)}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className={`
            lg:w-64 lg:flex-shrink-0 
            ${filtersOpen ? 'block' : 'hidden lg:block'}
          `}>
            <div className="sticky top-4">
              <ShopFilters
                filters={currentFilters}
                onFiltersChange={updateFilters}
                onClose={() => setFiltersOpen(false)}
              />
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {loading ? (
              <LoadingSkeleton />
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-600 mb-4">{error}</div>
                <button
                  onClick={fetchProducts}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : !data?.products.length ? (
              <EmptyState
                searchTerm={currentFilters.search}
                hasFilters={!!(currentFilters.category || currentFilters.style || currentFilters.priceRange?.min)}
                onClearFilters={() => router.push('/shop')}
              />
            ) : (
              <>
                <ProductGrid
                  products={data.products}
                  loading={false}
                />
                
                {/* Pagination */}
                {data.pagination.totalPages > 1 && (
                  <div className="mt-12 flex justify-center">
                    <nav className="flex space-x-2">
                      {/* Previous Button */}
                      <button
                        onClick={() => handlePageChange(data.pagination.page - 1)}
                        disabled={!data.pagination.hasPrev}
                        className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                      >
                        Previous
                      </button>

                      {/* Page Numbers */}
                      {Array.from({ length: Math.min(5, data.pagination.totalPages) }, (_, i) => {
                        const pageNum = Math.max(1, data.pagination.page - 2) + i
                        if (pageNum > data.pagination.totalPages) return null
                        
                        return (
                          <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            className={`px-4 py-2 border rounded-lg transition-colors ${
                              pageNum === data.pagination.page
                                ? 'bg-purple-600 text-white border-purple-600'
                                : 'border-gray-300 hover:bg-gray-50'
                            }`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}

                      {/* Next Button */}
                      <button
                        onClick={() => handlePageChange(data.pagination.page + 1)}
                        disabled={!data.pagination.hasNext}
                        className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                      >
                        Next
                      </button>
                    </nav>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}