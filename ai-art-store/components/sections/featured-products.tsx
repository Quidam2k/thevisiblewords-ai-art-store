'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ProductCard } from '@/components/product/product-card'
import { ProductWithArtwork } from '@/types'

export function FeaturedProducts() {
  const [products, setProducts] = useState<ProductWithArtwork[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual API call
    const fetchFeaturedProducts = async () => {
      try {
        // Simulated data for now
        const mockProducts: ProductWithArtwork[] = [
          {
            id: '1',
            artworkId: 'art1',
            printifyProductId: 'p1',
            title: 'Whimsical Forest Dreams',
            description: 'A magical forest scene with floating lights',
            basePrice: 2499,
            markupPercentage: 100,
            active: true,
            printifyBlueprintId: 3,
            printProviderId: 1,
            variants: null,
            images: ['/placeholder-art-1.jpg'],
            category: 'Wall Art',
            featured: true,
            createdAt: new Date(),
            updatedAt: new Date(),
            artwork: {
              id: 'art1',
              title: 'Whimsical Forest Dreams',
              description: 'A magical forest scene with floating lights',
              prompt: 'magical forest with glowing orbs and mystical creatures',
              fileUrl: '/placeholder-art-1.jpg',
              thumbnailUrl: '/placeholder-art-1-thumb.jpg',
              analysis: null,
              tags: ['fantasy', 'forest', 'magical'],
              style: 'WHIMSY' as const,
              active: true,
              createdAt: new Date(),
              updatedAt: new Date(),
            }
          },
          // Add more mock products...
        ]
        
        setProducts(mockProducts)
      } catch (error) {
        console.error('Error fetching featured products:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchFeaturedProducts()
  }, [])

  if (loading) {
    return (
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">Featured Products</h2>
            <p className="text-gray-600 mt-4">Discover our most popular AI-generated artwork</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg h-80 animate-pulse"></div>
            ))}
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Featured Products</h2>
          <p className="text-gray-600 mt-4">Discover our most popular AI-generated artwork</p>
        </div>

        {products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {products.slice(0, 4).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No featured products available yet.</p>
            <Link 
              href="/admin" 
              className="text-purple-600 hover:text-purple-700 font-medium mt-2 inline-block"
            >
              Add some products in the admin panel
            </Link>
          </div>
        )}

        <div className="text-center">
          <Link
            href="/shop"
            className="inline-flex items-center px-6 py-3 border border-purple-600 text-purple-600 font-medium rounded-lg hover:bg-purple-50 transition-colors"
          >
            View All Products
          </Link>
        </div>
      </div>
    </section>
  )
}