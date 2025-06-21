'use client'

import { useState } from 'react'
import { ProductWithArtwork } from '@/types'

interface ProductTabsProps {
  product: ProductWithArtwork
}

type TabType = 'details' | 'shipping' | 'care' | 'artwork'

export function ProductTabs({ product }: ProductTabsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('details')

  const tabs = [
    { id: 'details', label: 'Product Details' },
    { id: 'shipping', label: 'Shipping & Returns' },
    { id: 'care', label: 'Care Instructions' },
    { id: 'artwork', label: 'Artwork Info' },
  ] as const

  return (
    <div className="w-full">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8" aria-label="Product information tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-8">
        {activeTab === 'details' && (
          <div className="prose prose-gray max-w-none">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Product Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">General Information</h4>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Product Type:</dt>
                    <dd className="text-gray-900">Print-on-Demand Art</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Category:</dt>
                    <dd className="text-gray-900">{product.category || 'Art & Design'}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Print Quality:</dt>
                    <dd className="text-gray-900">High Resolution (300 DPI)</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Production:</dt>
                    <dd className="text-gray-900">Made to Order</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Available Products</h4>
                <div className="space-y-2 text-sm">
                  {product.variants && product.variants.length > 0 ? (
                    <ul className="space-y-1">
                      {Array.from(new Set(product.variants.map(v => v.type))).map((type) => (
                        <li key={type} className="text-gray-600">• {type}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-600">Multiple product types available</p>
                  )}
                </div>
              </div>
            </div>

            {product.description && (
              <div className="mt-6">
                <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                <p className="text-gray-600 leading-relaxed">{product.description}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'shipping' && (
          <div className="prose prose-gray max-w-none">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Shipping & Returns</h3>
            
            <div className="space-y-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Shipping Information</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• <strong>Free Standard Shipping</strong> on orders over $75</li>
                  <li>• Standard shipping: 5-7 business days</li>
                  <li>• Express shipping: 2-3 business days (additional cost)</li>
                  <li>• Production time: 2-5 business days before shipping</li>
                  <li>• International shipping available to most countries</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Return Policy</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• 30-day return window from delivery date</li>
                  <li>• Items must be in original, unused condition</li>
                  <li>• Custom/personalized items are not returnable</li>
                  <li>• Return shipping costs are customer's responsibility</li>
                  <li>• Refunds processed within 5-7 business days</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Order Tracking</h4>
                <p className="text-sm text-gray-600">
                  You'll receive a tracking number via email once your order ships. 
                  Track your package through our partner carriers.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'care' && (
          <div className="prose prose-gray max-w-none">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Care Instructions</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Apparel Care</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Machine wash cold with like colors</li>
                  <li>• Use non-chlorine bleach only when needed</li>
                  <li>• Tumble dry low heat</li>
                  <li>• Iron inside out on low heat</li>
                  <li>• Do not dry clean</li>
                  <li>• Turn garment inside out before washing</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Print Care</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Avoid direct sunlight for extended periods</li>
                  <li>• Handle with clean, dry hands</li>
                  <li>• Store in cool, dry place</li>
                  <li>• For framed prints: dust with soft, dry cloth</li>
                  <li>• For canvas: avoid moisture and humidity</li>
                </ul>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Care Tips</h4>
              <p className="text-sm text-blue-800">
                Proper care ensures your artwork stays vibrant for years to come. 
                The high-quality prints are designed to maintain their color and 
                clarity with normal use and proper care.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'artwork' && (
          <div className="prose prose-gray max-w-none">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Artwork Information</h3>
            
            <div className="space-y-6">
              {product.artwork && (
                <>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Art Details</h4>
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {product.artwork.style && (
                        <div>
                          <dt className="font-medium text-gray-900">Style:</dt>
                          <dd className="text-gray-600 mt-1">{product.artwork.style}</dd>
                        </div>
                      )}
                      <div>
                        <dt className="font-medium text-gray-900">Creation Method:</dt>
                        <dd className="text-gray-600 mt-1">AI-Generated Digital Art</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-900">Resolution:</dt>
                        <dd className="text-gray-600 mt-1">High Resolution (300+ DPI)</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-900">Color Profile:</dt>
                        <dd className="text-gray-600 mt-1">sRGB (optimized for printing)</dd>
                      </div>
                    </dl>
                  </div>

                  {product.artwork.analysis && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Art Analysis</h4>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {product.artwork.analysis}
                      </p>
                    </div>
                  )}

                  {product.artwork.tags && product.artwork.tags.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Artistic Elements</h4>
                      <div className="flex flex-wrap gap-2">
                        {product.artwork.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {product.artwork.originalPrompt && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Original Prompt</h4>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-700 font-mono leading-relaxed">
                          "{product.artwork.originalPrompt}"
                        </p>
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="border-t border-gray-200 pt-6">
                <h4 className="font-medium text-gray-900 mb-2">Usage Rights</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>• Personal use license included with purchase</p>
                  <p>• Commercial licensing available separately</p>
                  <p>• High-resolution files available for certain products</p>
                  <p>• Copyright remains with The Visible Words</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}