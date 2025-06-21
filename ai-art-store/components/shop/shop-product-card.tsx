'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { HeartIcon, ShoppingBagIcon } from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid'
import { ProductWithArtwork, CartItem } from '@/types'
import { formatPrice, generateId } from '@/lib/utils'
import { useCart } from '@/hooks/use-cart'

interface ShopProductCardProps {
  product: ProductWithArtwork
}

export function ShopProductCard({ product }: ShopProductCardProps) {
  const [imageError, setImageError] = useState(false)
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [addingToCart, setAddingToCart] = useState(false)
  const { addItem } = useCart()

  const displayPrice = formatPrice(product.basePrice)
  const styleColor = {
    WHIMSY: 'bg-blue-100 text-blue-800',
    EPIC: 'bg-red-100 text-red-800',
    HYBRID: 'bg-purple-100 text-purple-800',
  }[product.artwork.style]

  // Get the first available variant for quick add to cart
  const defaultVariant = product.variants && Array.isArray(product.variants) 
    ? product.variants[0] 
    : { id: 1, price: product.basePrice, title: 'Default', options: {}, available: true }

  const handleQuickAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault() // Prevent navigation to product page
    e.stopPropagation()

    if (!defaultVariant) return

    setAddingToCart(true)

    try {
      const cartItem: CartItem = {
        id: generateId(),
        productId: product.id,
        title: product.title,
        price: defaultVariant.price || product.basePrice,
        quantity: 1,
        variant: {
          id: defaultVariant.id,
          title: defaultVariant.title,
          options: defaultVariant.options || {},
        },
        image: product.images[0] || '/images/placeholder-product.jpg',
        artworkStyle: product.artwork.style,
      }

      addItem(cartItem)
      
      // TODO: Show success toast notification
      console.log('Added to cart:', cartItem)
      
    } catch (error) {
      console.error('Error adding to cart:', error)
      // TODO: Show error toast notification
    } finally {
      setAddingToCart(false)
    }
  }

  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsWishlisted(!isWishlisted)
    // TODO: Integrate with wishlist API
  }

  return (
    <Link 
      href={`/product/${product.id}`}
      className="group block bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
    >
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        {!imageError && product.images[0] ? (
          <Image
            src={product.images[0]}
            alt={product.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setImageError(true)}
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
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
        
        {/* Overlay Actions */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
          <div className="flex gap-2">
            {/* Quick Add to Cart */}
            <button
              onClick={handleQuickAddToCart}
              disabled={addingToCart}
              className="bg-white text-gray-900 p-2 rounded-full shadow-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Quick add to cart"
            >
              <ShoppingBagIcon className="h-5 w-5" />
            </button>

            {/* Wishlist Toggle */}
            <button
              onClick={handleWishlistToggle}
              className="bg-white text-gray-900 p-2 rounded-full shadow-lg hover:bg-gray-50 transition-colors"
              title={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
            >
              {isWishlisted ? (
                <HeartSolidIcon className="h-5 w-5 text-red-500" />
              ) : (
                <HeartIcon className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

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
        <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors line-clamp-2 mb-2">
          {product.title}
        </h3>
        
        {product.description && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">
            {product.description}
          </p>
        )}

        <div className="flex items-center justify-between mb-3">
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
          <div className="flex flex-wrap gap-1">
            {product.artwork.tags.slice(0, 3).map((tag) => (
              <span 
                key={tag} 
                className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded hover:bg-gray-100 transition-colors"
              >
                #{tag}
              </span>
            ))}
            {product.artwork.tags.length > 3 && (
              <span className="text-xs text-gray-400">
                +{product.artwork.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Variant Count */}
        {product.variants && Array.isArray(product.variants) && product.variants.length > 1 && (
          <div className="mt-2 text-xs text-gray-500">
            {product.variants.length} variants available
          </div>
        )}
      </div>
    </Link>
  )
}