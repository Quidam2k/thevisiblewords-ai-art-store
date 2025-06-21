'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { ProductFilters } from '@/types'

interface ShopFiltersProps {
  filters: ProductFilters
  onFiltersChange: (filters: Partial<ProductFilters>) => void
  onClose?: () => void
}

interface CategoryData {
  categories: Array<{ name: string; slug: string; count: number }>
  styles: Array<{ name: string; slug: string; count: number }>
  priceRange: { min: number; max: number }
  popularTags: Array<{ tag: string; count: number }>
}

export function ShopFilters({ filters, onFiltersChange, onClose }: ShopFiltersProps) {
  const [categoryData, setCategoryData] = useState<CategoryData | null>(null)
  const [priceRange, setPriceRange] = useState({
    min: filters.priceRange?.min || 0,
    max: filters.priceRange?.max || 10000,
  })

  useEffect(() => {
    fetchCategoryData()
  }, [])

  const fetchCategoryData = async () => {
    try {
      const response = await fetch('/api/categories')
      if (response.ok) {
        const data = await response.json()
        setCategoryData(data)
        
        // Set default price range if not already set
        if (!filters.priceRange?.min && !filters.priceRange?.max) {
          setPriceRange({
            min: data.priceRange.min,
            max: data.priceRange.max,
          })
        }
      }
    } catch (error) {
      console.error('Error fetching category data:', error)
    }
  }

  const handlePriceRangeChange = () => {
    onFiltersChange({
      priceRange: {
        min: priceRange.min,
        max: priceRange.max,
      }
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      category: undefined,
      style: undefined,
      priceRange: undefined,
      tags: [],
    })
    if (categoryData) {
      setPriceRange({
        min: categoryData.priceRange.min,
        max: categoryData.priceRange.max,
      })
    }
  }

  const hasActiveFilters = !!(
    filters.category || 
    filters.style || 
    filters.priceRange?.min || 
    filters.priceRange?.max ||
    (filters.tags && filters.tags.length > 0)
  )

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-purple-600 hover:text-purple-700 transition-colors"
            >
              Clear all
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {/* Categories */}
        {categoryData?.categories && categoryData.categories.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Category</h4>
            <div className="space-y-2">
              {categoryData.categories.map((category) => (
                <label key={category.slug} className="flex items-center">
                  <input
                    type="radio"
                    name="category"
                    value={category.name}
                    checked={filters.category === category.name}
                    onChange={(e) => onFiltersChange({ 
                      category: e.target.checked ? category.name : undefined 
                    })}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {category.name} ({category.count})
                  </span>
                </label>
              ))}
              {filters.category && (
                <button
                  onClick={() => onFiltersChange({ category: undefined })}
                  className="text-sm text-purple-600 hover:text-purple-700 transition-colors"
                >
                  Clear category
                </button>
              )}
            </div>
          </div>
        )}

        {/* Styles */}
        {categoryData?.styles && categoryData.styles.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Art Style</h4>
            <div className="space-y-2">
              {categoryData.styles.map((style) => (
                <label key={style.slug} className="flex items-center">
                  <input
                    type="radio"
                    name="style"
                    value={style.name}
                    checked={filters.style === style.name}
                    onChange={(e) => onFiltersChange({ 
                      style: e.target.checked ? style.name as any : undefined 
                    })}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {style.name.charAt(0) + style.name.slice(1).toLowerCase()} ({style.count})
                  </span>
                </label>
              ))}
              {filters.style && (
                <button
                  onClick={() => onFiltersChange({ style: undefined })}
                  className="text-sm text-purple-600 hover:text-purple-700 transition-colors"
                >
                  Clear style
                </button>
              )}
            </div>
          </div>
        )}

        {/* Price Range */}
        {categoryData?.priceRange && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Price Range</h4>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={priceRange.min}
                  onChange={(e) => setPriceRange(prev => ({ 
                    ...prev, 
                    min: parseInt(e.target.value) || 0 
                  }))}
                  onBlur={handlePriceRangeChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <span className="text-gray-400">to</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={priceRange.max}
                  onChange={(e) => setPriceRange(prev => ({ 
                    ...prev, 
                    max: parseInt(e.target.value) || 10000 
                  }))}
                  onBlur={handlePriceRangeChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              {/* Price presets */}
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Under $25', min: 0, max: 2500 },
                  { label: '$25 - $50', min: 2500, max: 5000 },
                  { label: '$50 - $100', min: 5000, max: 10000 },
                  { label: 'Over $100', min: 10000, max: 99999 },
                ].map((preset) => (
                  <button
                    key={preset.label}
                    onClick={() => {
                      setPriceRange({ min: preset.min, max: preset.max })
                      onFiltersChange({
                        priceRange: { min: preset.min, max: preset.max }
                      })
                    }}
                    className="text-xs px-2 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 transition-colors"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
              
              {(filters.priceRange?.min || filters.priceRange?.max) && (
                <button
                  onClick={() => {
                    onFiltersChange({ priceRange: undefined })
                    if (categoryData) {
                      setPriceRange({
                        min: categoryData.priceRange.min,
                        max: categoryData.priceRange.max,
                      })
                    }
                  }}
                  className="text-sm text-purple-600 hover:text-purple-700 transition-colors"
                >
                  Clear price filter
                </button>
              )}
            </div>
          </div>
        )}

        {/* Popular Tags */}
        {categoryData?.popularTags && categoryData.popularTags.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Popular Tags</h4>
            <div className="flex flex-wrap gap-2">
              {categoryData.popularTags.slice(0, 10).map((tagItem) => (
                <button
                  key={tagItem.tag}
                  onClick={() => {
                    const currentTags = filters.tags || []
                    const isSelected = currentTags.includes(tagItem.tag)
                    const newTags = isSelected
                      ? currentTags.filter(t => t !== tagItem.tag)
                      : [...currentTags, tagItem.tag]
                    onFiltersChange({ tags: newTags })
                  }}
                  className={`text-xs px-2 py-1 rounded transition-colors ${
                    filters.tags?.includes(tagItem.tag)
                      ? 'bg-purple-100 text-purple-800 border border-purple-200'
                      : 'bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  #{tagItem.tag} ({tagItem.count})
                </button>
              ))}
            </div>
            {filters.tags && filters.tags.length > 0 && (
              <button
                onClick={() => onFiltersChange({ tags: [] })}
                className="text-sm text-purple-600 hover:text-purple-700 transition-colors mt-2"
              >
                Clear tags
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}