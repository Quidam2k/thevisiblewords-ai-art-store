'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ProductWithArtwork } from '@/types'
import { formatPrice } from '@/lib/utils'

interface ProductCardProps {
  product: ProductWithArtwork
}

export function ProductCard({ product }: ProductCardProps) {
  const [imageError, setImageError] = useState(false)

  const displayPrice = formatPrice(product.basePrice)
  const styleColor = {
    WHIMSY: 'bg-blue-100 text-blue-800',
    EPIC: 'bg-red-100 text-red-800',
    HYBRID: 'bg-purple-100 text-purple-800',
  }[product.artwork.style]

  return (
    <Link 
      href={`/product/${product.id}`}
      className="group block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
    >
      <div className="relative aspect-square overflow-hidden rounded-t-lg bg-gray-100">
        {!imageError && product.images[0] ? (
          <Image
            src={product.images[0]}
            alt={product.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex items-center justify-center h-full bg-gradient-to-br from-gray-100 to-gray-200">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-2 bg-gray-300 rounded-lg flex items-center justify-center">
                <svg 
                  className="w-8 h-8 text-gray-400" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                  />
                </svg>
              </div>
              <p className="text-sm text-gray-500">Art Preview</p>
            </div>
          </div>
        )}
        
        {/* Style Badge */}
        <div className="absolute top-2 left-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${styleColor}`}>
            {product.artwork.style}
          </span>
        </div>

        {/* Featured Badge */}
        {product.featured && (
          <div className="absolute top-2 right-2">
            <span className="bg-yellow-100 text-yellow-800 px-2 py-1 text-xs font-medium rounded-full">
              Featured
            </span>
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors line-clamp-2">
          {product.title}
        </h3>
        
        {product.description && (
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {product.description}
          </p>
        )}

        <div className="flex items-center justify-between mt-3">
          <span className="text-lg font-bold text-gray-900">
            {displayPrice}
          </span>
          
          {product.category && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {product.category}
            </span>
          )}
        </div>

        {/* Tags */}
        {product.artwork.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {product.artwork.tags.slice(0, 3).map((tag) => (
              <span 
                key={tag} 
                className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded"
              >
                #{tag}
              </span>
            ))}
            {product.artwork.tags.length > 3 && (
              <span className="text-xs text-gray-400">
                +{product.artwork.tags.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>
    </Link>
  )
}