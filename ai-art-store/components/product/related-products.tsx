'use client'

import { useState } from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import { ProductCard } from '@/components/product/product-card'
import { ProductWithArtwork } from '@/types'

interface RelatedProductsProps {
  products: ProductWithArtwork[]
  currentProductId: string
}

export function RelatedProducts({ products, currentProductId }: RelatedProductsProps) {
  const [startIndex, setStartIndex] = useState(0)
  
  // Filter out current product and limit to reasonable number
  const filteredProducts = products
    .filter(product => product.id !== currentProductId)
    .slice(0, 12)
  
  if (filteredProducts.length === 0) {
    return null
  }
  
  const itemsPerPage = 4
  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage)
  const currentPage = Math.floor(startIndex / itemsPerPage)
  const canGoBack = startIndex > 0
  const canGoForward = startIndex + itemsPerPage < filteredProducts.length
  
  const visibleProducts = filteredProducts.slice(startIndex, startIndex + itemsPerPage)
  
  const goToPrevious = () => {
    setStartIndex(Math.max(0, startIndex - itemsPerPage))
  }
  
  const goToNext = () => {
    setStartIndex(Math.min(filteredProducts.length - itemsPerPage, startIndex + itemsPerPage))
  }
  
  const goToPage = (page: number) => {
    setStartIndex(page * itemsPerPage)
  }

  return (
    <section className="border-t border-gray-200 pt-16">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-gray-900">You Might Also Like</h2>
        
        {/* Navigation Controls */}
        {filteredProducts.length > itemsPerPage && (
          <div className="flex items-center space-x-2">
            <button
              onClick={goToPrevious}
              disabled={!canGoBack}
              className="p-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Previous products"
            >
              <ChevronLeftIcon className="w-5 h-5" />
            </button>
            
            {/* Page Indicators */}
            <div className="flex space-x-1">
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i}
                  onClick={() => goToPage(i)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                    i === currentPage
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            
            <button
              onClick={goToNext}
              disabled={!canGoForward}
              className="p-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Next products"
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
      
      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {visibleProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            className="h-full"
          />
        ))}
      </div>
      
      {/* Mobile Navigation */}
      {filteredProducts.length > itemsPerPage && (
        <div className="flex justify-center mt-8 lg:hidden">
          <div className="flex items-center space-x-4">
            <button
              onClick={goToPrevious}
              disabled={!canGoBack}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeftIcon className="w-4 h-4 mr-2" />
              Previous
            </button>
            
            <span className="text-sm text-gray-600">
              {currentPage + 1} of {totalPages}
            </span>
            
            <button
              onClick={goToNext}
              disabled={!canGoForward}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRightIcon className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      )}
      
      {/* View All Link */}
      <div className="text-center mt-8">
        <a
          href="/shop"
          className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          View All Products
          <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </a>
      </div>
    </section>
  )
}