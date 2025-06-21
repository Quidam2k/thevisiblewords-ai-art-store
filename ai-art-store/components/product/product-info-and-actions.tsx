'use client'

import { useState } from 'react'
import { ProductInfo } from './product-info'
import { VariantSelector } from './variant-selector'
import { AddToCartSection } from './add-to-cart-section'
import { ProductWithArtwork, ProductVariant } from '@/types'

interface ProductInfoAndActionsProps {
  product: ProductWithArtwork
}

export function ProductInfoAndActions({ product }: ProductInfoAndActionsProps) {
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null)

  return (
    <div className="space-y-8">
      <ProductInfo product={product} />
      
      <VariantSelector
        product={product}
        onVariantChange={setSelectedVariant}
      />
      
      <AddToCartSection
        product={product}
        selectedVariant={selectedVariant}
      />
    </div>
  )
}