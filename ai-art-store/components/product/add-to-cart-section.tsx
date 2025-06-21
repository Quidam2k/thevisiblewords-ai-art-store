'use client'

import { useState, useEffect } from 'react'
import { ShoppingCartIcon, HeartIcon, ShareIcon } from '@heroicons/react/24/outline'
import { CheckIcon } from '@heroicons/react/24/solid'
import { ProductWithArtwork, ProductVariant } from '@/types'
import { useCart } from '@/hooks/use-cart'

interface AddToCartSectionProps {
  product: ProductWithArtwork
  selectedVariant?: ProductVariant | null
}

export function AddToCartSection({ product, selectedVariant }: AddToCartSectionProps) {
  const [quantity, setQuantity] = useState(1)
  const [isAdding, setIsAdding] = useState(false)
  const [isAdded, setIsAdded] = useState(false)
  const [currentVariant, setCurrentVariant] = useState<ProductVariant | null>(selectedVariant || null)
  
  const { addToCart } = useCart()
  
  useEffect(() => {
    setCurrentVariant(selectedVariant || null)
  }, [selectedVariant])

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity >= 1 && newQuantity <= 10) {
      setQuantity(newQuantity)
    }
  }

  const handleAddToCart = async () => {
    if (!currentVariant) {
      // Show error message that variant must be selected
      return
    }

    setIsAdding(true)
    
    try {
      // Add to cart using the cart context
      addToCart({
        productId: product.id,
        variantId: currentVariant.id,
        quantity: quantity,
        product: {
          id: product.id,
          title: product.title,
          price: currentVariant.price,
          image: product.images?.[0]?.url || '/placeholder-product.jpg',
          variant: {
            size: currentVariant.size,
            color: currentVariant.color,
            type: currentVariant.type,
          },
        },
      })
      
      setIsAdded(true)
      setTimeout(() => setIsAdded(false), 2000)
      
    } catch (error) {
      console.error('Error adding to cart:', error)
      // You could add error toast here
    } finally {
      setIsAdding(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const totalPrice = currentVariant ? currentVariant.price * quantity : product.basePrice * quantity

  return (
    <div className="space-y-6">
      {/* Quantity Selection */}
      <div>
        <label htmlFor="quantity" className="block text-sm font-medium text-gray-900 mb-3">
          Quantity
        </label>
        <div className="flex items-center space-x-4">
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={() => handleQuantityChange(quantity - 1)}
              disabled={quantity <= 1}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            <input
              type="number"
              id="quantity"
              min="1"
              max="10"
              value={quantity}
              onChange={(e) => handleQuantityChange(parseInt(e.target.value) || 1)}
              className="w-16 px-3 py-2 text-center border-0 focus:ring-0 focus:outline-none"
            />
            <button
              onClick={() => handleQuantityChange(quantity + 1)}
              disabled={quantity >= 10}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
          </div>
          <div className="text-sm text-gray-600">
            Maximum 10 items per order
          </div>
        </div>
      </div>

      {/* Total Price */}
      <div className="border-t border-gray-200 pt-6">
        <div className="flex items-center justify-between text-lg">
          <span className="font-medium text-gray-900">Total:</span>
          <span className="font-bold text-gray-900">
            {formatPrice(totalPrice)}
          </span>
        </div>
        {quantity > 1 && currentVariant && (
          <p className="text-sm text-gray-600 mt-1">
            {formatPrice(currentVariant.price)} × {quantity}
          </p>
        )}
      </div>

      {/* Add to Cart Button */}
      <div className="space-y-4">
        <button
          onClick={handleAddToCart}
          disabled={!currentVariant || !currentVariant.available || isAdding}
          className={`w-full flex items-center justify-center px-8 py-4 border border-transparent rounded-lg text-base font-medium transition-colors ${
            !currentVariant || !currentVariant.available
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : isAdded
              ? 'bg-green-600 text-white'
              : 'bg-purple-600 text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500'
          }`}
        >
          {isAdding ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Adding to Cart...
            </>
          ) : isAdded ? (
            <>
              <CheckIcon className="w-5 h-5 mr-2" />
              Added to Cart!
            </>
          ) : !currentVariant ? (
            'Select Options'
          ) : !currentVariant.available ? (
            'Out of Stock'
          ) : (
            <>
              <ShoppingCartIcon className="w-5 h-5 mr-2" />
              Add to Cart
            </>
          )}
        </button>

        {/* Secondary Actions */}
        <div className="flex space-x-4">
          <button className="flex-1 flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            <HeartIcon className="w-5 h-5 mr-2" />
            Add to Wishlist
          </button>
          <button className="flex-1 flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            <ShareIcon className="w-5 h-5 mr-2" />
            Share
          </button>
        </div>
      </div>

      {/* Validation Messages */}
      {!currentVariant && (
        <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
          <p className="text-sm text-yellow-800">
            Please select all product options before adding to cart.
          </p>
        </div>
      )}

      {currentVariant && !currentVariant.available && (
        <div className="border border-red-200 rounded-lg p-4 bg-red-50">
          <p className="text-sm text-red-800">
            This variant is currently out of stock. Please select a different option or check back later.
          </p>
        </div>
      )}

      {/* Purchase Information */}
      <div className="border-t border-gray-200 pt-6 text-sm text-gray-600 space-y-2">
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Free shipping on orders over $75</span>
        </div>
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>30-day return policy</span>
        </div>
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Print-on-demand • Made to order</span>
        </div>
      </div>
    </div>
  )
}