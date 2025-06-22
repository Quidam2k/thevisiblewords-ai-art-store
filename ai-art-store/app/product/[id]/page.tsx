import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { ProductGallery } from '@/components/product/product-gallery'
import { ProductInfoAndActions } from '@/components/product/product-info-and-actions'
import { ProductTabs } from '@/components/product/product-tabs'
import { RelatedProducts } from '@/components/product/related-products'
import { ProductWithArtwork } from '@/types'

interface ProductPageProps {
  params: Promise<{
    id: string
  }>
}

async function getProduct(id: string): Promise<ProductWithArtwork | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/products/${id}`, {
      cache: 'no-store', // Always fetch fresh data
    })
    
    if (!res.ok) {
      return null
    }
    
    const data = await res.json()
    return data.product
  } catch (error) {
    console.error('Error fetching product:', error)
    return null
  }
}

async function getRelatedProducts(productId: string, category?: string, style?: string): Promise<ProductWithArtwork[]> {
  try {
    const params = new URLSearchParams({
      limit: '6',
      exclude: productId,
    })
    
    if (category) params.set('category', category)
    if (style) params.set('style', style)
    
    const res = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/products?${params.toString()}`, {
      cache: 'no-store',
    })
    
    if (!res.ok) {
      return []
    }
    
    const data = await res.json()
    return data.products || []
  } catch (error) {
    console.error('Error fetching related products:', error)
    return []
  }
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const { id } = await params
  const product = await getProduct(id)
  
  if (!product) {
    return {
      title: 'Product Not Found - The Visible Words',
    }
  }
  
  return {
    title: `${product.title} - The Visible Words`,
    description: product.description || `${product.title} - AI-generated art available on various products`,
    openGraph: {
      title: product.title,
      description: product.description || `${product.title} - AI-generated art`,
      images: [
        {
          url: product.images?.[0]?.url || '/placeholder-product.jpg',
          width: 800,
          height: 600,
          alt: product.title,
        },
      ],
    },
  }
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params
  const product = await getProduct(id)
  
  if (!product) {
    notFound()
  }
  
  const relatedProducts = await getRelatedProducts(
    product.id,
    product.category,
    product.artwork?.style
  )
  
  return (
    <div className="min-h-screen bg-white">
      {/* Breadcrumb */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li>
            <a href="/" className="hover:text-gray-700 transition-colors">
              Home
            </a>
          </li>
          <li className="flex items-center">
            <span className="mx-2">/</span>
            <a href="/shop" className="hover:text-gray-700 transition-colors">
              Shop
            </a>
          </li>
          {product.category && (
            <li className="flex items-center">
              <span className="mx-2">/</span>
              <a 
                href={`/shop?category=${encodeURIComponent(product.category)}`}
                className="hover:text-gray-700 transition-colors"
              >
                {product.category}
              </a>
            </li>
          )}
          <li className="flex items-center">
            <span className="mx-2">/</span>
            <span className="text-gray-900 font-medium">{product.title}</span>
          </li>
        </ol>
      </nav>

      {/* Main Product Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Product Gallery */}
          <div className="space-y-4">
            <ProductGallery
              images={product.images || []}
              title={product.title}
            />
          </div>

          {/* Product Info & Actions */}
          <ProductInfoAndActions product={product} />
        </div>

        {/* Product Tabs */}
        <div className="mb-16">
          <ProductTabs
            product={product}
          />
        </div>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <RelatedProducts
            products={relatedProducts}
            currentProductId={product.id}
          />
        )}
      </div>
    </div>
  )
}