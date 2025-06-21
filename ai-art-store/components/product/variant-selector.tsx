'use client'

import { useState, useEffect } from 'react'
import { CheckIcon } from '@heroicons/react/24/solid'
import { ProductWithArtwork, ProductVariant } from '@/types'

interface VariantSelectorProps {
  product: ProductWithArtwork
  onVariantChange?: (variant: ProductVariant | null) => void
}

export function VariantSelector({ product, onVariantChange }: VariantSelectorProps) {
  const [selectedSize, setSelectedSize] = useState<string>('')
  const [selectedColor, setSelectedColor] = useState<string>('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null)
  
  // Extract unique options from variants
  const sizes = Array.from(new Set(product.variants?.map(v => v.size).filter(Boolean))) || []
  const colors = Array.from(new Set(product.variants?.map(v => v.color).filter(Boolean))) || []
  const types = Array.from(new Set(product.variants?.map(v => v.type).filter(Boolean))) || []
  
  // Set default selections
  useEffect(() => {
    if (sizes.length > 0 && !selectedSize) {
      setSelectedSize(sizes[0])
    }
    if (colors.length > 0 && !selectedColor) {
      setSelectedColor(colors[0])
    }
    if (types.length > 0 && !selectedType) {
      setSelectedType(types[0])
    }
  }, [sizes, colors, types, selectedSize, selectedColor, selectedType])
  
  // Find matching variant when selections change
  useEffect(() => {
    if (product.variants && selectedSize && selectedColor && selectedType) {
      const variant = product.variants.find(v => 
        v.size === selectedSize && 
        v.color === selectedColor && 
        v.type === selectedType
      )
      setSelectedVariant(variant || null)
      onVariantChange?.(variant || null)
    } else {
      setSelectedVariant(null)
      onVariantChange?.(null)
    }
  }, [selectedSize, selectedColor, selectedType, product.variants, onVariantChange])
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }
  
  const getColorSwatch = (color: string) => {
    const colorMap: { [key: string]: string } = {
      white: '#FFFFFF',
      black: '#000000',
      red: '#EF4444',
      blue: '#3B82F6',
      green: '#10B981',
      yellow: '#F59E0B',
      purple: '#8B5CF6',
      pink: '#EC4899',
      gray: '#6B7280',
      navy: '#1E3A8A',
      maroon: '#7F1D1D',
      olive: '#365314',
    }
    
    return colorMap[color.toLowerCase()] || '#9CA3AF'
  }
  
  const getSizeDisplayName = (size: string) => {
    const sizeMap: { [key: string]: string } = {
      xs: 'XS',
      s: 'S',
      m: 'M',
      l: 'L',
      xl: 'XL',
      xxl: 'XXL',
      '3xl': '3XL',
    }
    
    return sizeMap[size.toLowerCase()] || size.toUpperCase()
  }
  
  const getTypeDisplayName = (type: string) => {
    const typeMap: { [key: string]: string } = {
      tshirt: 'T-Shirt',
      hoodie: 'Hoodie',
      poster: 'Poster',
      mug: 'Mug',
      canvas: 'Canvas Print',
      sticker: 'Sticker',
      totebag: 'Tote Bag',
    }
    
    return typeMap[type.toLowerCase()] || type
  }

  if (!product.variants || product.variants.length === 0) {
    return (
      <div className="border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Product Options</h3>
        <p className="text-gray-600">No variants available for this product.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Product Type Selection */}
      {types.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Product Type</h3>
          <div className="grid grid-cols-2 gap-3">
            {types.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`relative border rounded-lg p-4 text-left transition-colors ${
                  selectedType === type
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    {getTypeDisplayName(type)}
                  </span>
                  {selectedType === type && (
                    <CheckIcon className="w-5 h-5 text-purple-600" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Size Selection */}
      {sizes.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Size</h3>
          <div className="flex flex-wrap gap-3">
            {sizes.map((size) => (
              <button
                key={size}
                onClick={() => setSelectedSize(size)}
                className={`relative min-w-[3rem] px-4 py-2 text-sm font-medium border rounded-lg transition-colors ${
                  selectedSize === size
                    ? 'border-purple-600 bg-purple-600 text-white'
                    : 'border-gray-200 text-gray-900 hover:border-gray-300'
                }`}
              >
                {getSizeDisplayName(size)}
                {selectedSize === size && (
                  <CheckIcon className="absolute -top-1 -right-1 w-4 h-4 text-white bg-purple-600 rounded-full p-0.5" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Color Selection */}
      {colors.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Color</h3>
          <div className="flex flex-wrap gap-3">
            {colors.map((color) => (
              <button
                key={color}
                onClick={() => setSelectedColor(color)}
                className={`relative group flex items-center space-x-3 border rounded-lg p-3 transition-colors ${
                  selectedColor === color
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full border-2 ${
                    color.toLowerCase() === 'white' ? 'border-gray-300' : 'border-gray-200'
                  }`}
                  style={{ backgroundColor: getColorSwatch(color) }}
                />
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {color}
                </span>
                {selectedColor === color && (
                  <CheckIcon className="w-5 h-5 text-purple-600" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Price Display */}
      {selectedVariant && (
        <div className="border-t border-gray-200 pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Selected variant price:</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatPrice(selectedVariant.price)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Availability:</p>
              <p className={`font-medium ${
                selectedVariant.available 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {selectedVariant.available ? 'In Stock' : 'Out of Stock'}
              </p>
            </div>
          </div>
          
          {/* Variant Details */}
          <div className="mt-4 text-sm text-gray-600">
            <p>
              <span className="font-medium">Selected:</span> {' '}
              {getTypeDisplayName(selectedType)} • {' '}
              {getSizeDisplayName(selectedSize)} • {' '}
              <span className="capitalize">{selectedColor}</span>
            </p>
            {selectedVariant.printifyProductId && (
              <p className="mt-1">
                <span className="font-medium">Product ID:</span> {' '}
                <span className="font-mono">{selectedVariant.printifyProductId}</span>
              </p>
            )}
          </div>
        </div>
      )}

      {/* Selection Validation */}
      {(!selectedSize || !selectedColor || !selectedType) && (
        <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
          <p className="text-sm text-yellow-800">
            Please select all options to see pricing and availability.
          </p>
        </div>
      )}
    </div>
  )
}