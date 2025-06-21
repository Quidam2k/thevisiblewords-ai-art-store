'use client'

import { useState } from 'react'
import { HeartIcon, ShareIcon } from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid'
import { ProductWithArtwork } from '@/types'

interface ProductInfoProps {
  product: ProductWithArtwork
}

export function ProductInfo({ product }: ProductInfoProps) {
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [shareMenuOpen, setShareMenuOpen] = useState(false)
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const getStyleBadgeColor = (style: string) => {
    switch (style?.toLowerCase()) {
      case 'whimsy':
        return 'bg-pink-100 text-pink-800 border-pink-200'
      case 'epic':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'hybrid':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: product.title,
          text: product.description || `Check out this amazing AI art: ${product.title}`,
          url: window.location.href,
        })
      } catch (error) {
        console.error('Error sharing:', error)
        setShareMenuOpen(true)
      }
    } else {
      setShareMenuOpen(true)
    }
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setShareMenuOpen(false)
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Product Title & Actions */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {product.title}
          </h1>
          
          {/* Style Badge */}
          {product.artwork?.style && (
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStyleBadgeColor(product.artwork.style)}`}>
              {product.artwork.style}
            </span>
          )}
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => setIsWishlisted(!isWishlisted)}
            className="p-2 text-gray-400 hover:text-red-500 transition-colors"
            aria-label={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
          >
            {isWishlisted ? (
              <HeartSolidIcon className="w-6 h-6 text-red-500" />
            ) : (
              <HeartIcon className="w-6 h-6" />
            )}
          </button>
          
          <div className="relative">
            <button
              onClick={handleShare}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Share product"
            >
              <ShareIcon className="w-6 h-6" />
            </button>
            
            {/* Share Dropdown */}
            {shareMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="p-2">
                  <button
                    onClick={copyToClipboard}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    Copy link
                  </button>
                  <a
                    href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(product.title)}&url=${encodeURIComponent(window.location.href)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    Share on Twitter
                  </a>
                  <a
                    href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    Share on Facebook
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Price */}
      <div className="space-y-2">
        <div className="text-3xl font-bold text-gray-900">
          {formatPrice(product.basePrice)}
        </div>
        <p className="text-sm text-gray-600">
          Starting price • Final price varies by product type and size
        </p>
      </div>

      {/* Description */}
      {product.description && (
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {product.description}
          </p>
        </div>
      )}

      {/* Product Details */}
      <div className="border-t border-gray-200 pt-6 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          {product.category && (
            <div>
              <span className="font-medium text-gray-900">Category:</span>
              <span className="ml-2 text-gray-600">{product.category}</span>
            </div>
          )}
          
          {product.artwork?.style && (
            <div>
              <span className="font-medium text-gray-900">Art Style:</span>
              <span className="ml-2 text-gray-600">{product.artwork.style}</span>
            </div>
          )}
          
          <div>
            <span className="font-medium text-gray-900">Product ID:</span>
            <span className="ml-2 text-gray-600 font-mono">{product.id}</span>
          </div>
          
          <div>
            <span className="font-medium text-gray-900">Available Since:</span>
            <span className="ml-2 text-gray-600">
              {new Date(product.createdAt).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      {/* Tags */}
      {product.artwork?.tags && product.artwork.tags.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {product.artwork.tags.slice(0, 8).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
              >
                {tag}
              </span>
            ))}
            {product.artwork.tags.length > 8 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                +{product.artwork.tags.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Artwork Analysis */}
      {product.artwork?.analysis && (
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Art Analysis</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            {product.artwork.analysis}
          </p>
        </div>
      )}
    </div>
  )
}