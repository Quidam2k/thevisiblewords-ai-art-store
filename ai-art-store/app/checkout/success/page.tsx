'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useCart } from '@/hooks/use-cart'

export default function CheckoutSuccessPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const { clearCart } = useCart()
  const [orderDetails, setOrderDetails] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (sessionId) {
      // Clear the cart
      clearCart()
      
      // Fetch order details (optional)
      fetchOrderDetails(sessionId)
    } else {
      setLoading(false)
    }
  }, [sessionId, clearCart])

  const fetchOrderDetails = async (sessionId: string) => {
    try {
      // You could implement an API endpoint to fetch order details
      // For now, we'll just set loading to false
      setLoading(false)
    } catch (error) {
      console.error('Error fetching order details:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Processing your order...</p>
        </div>
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Invalid Order</h1>
          <p className="text-gray-600 mb-8">We couldn't find your order details.</p>
          <Link
            href="/shop"
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center">
        {/* Success Icon */}
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
          <svg
            className="h-8 w-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Order Confirmed!
        </h1>
        
        <p className="text-lg text-gray-600 mb-8">
          Thank you for your purchase. We've received your order and will start processing it right away.
        </p>

        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">What happens next?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div className="text-center">
              <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-2 font-semibold">
                1
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Order Processing</h3>
              <p className="text-gray-600">We'll prepare your custom prints with care</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-2 font-semibold">
                2
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Production</h3>
              <p className="text-gray-600">Your items are printed using premium materials</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-2 font-semibold">
                3
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Shipping</h3>
              <p className="text-gray-600">Your order ships within 3-5 business days</p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <p className="text-sm text-blue-800">
            <strong>Order confirmation:</strong> You'll receive an email confirmation shortly with your order details and tracking information.
          </p>
        </div>

        <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
          <Link
            href="/shop"
            className="block w-full sm:w-auto bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors text-center"
          >
            Continue Shopping
          </Link>
          <Link
            href="/about"
            className="block w-full sm:w-auto border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors text-center"
          >
            Learn More About Us
          </Link>
        </div>

        <div className="mt-12 text-sm text-gray-500">
          <p>Need help? <Link href="/contact" className="text-purple-600 hover:text-purple-700">Contact our support team</Link></p>
        </div>
      </div>
    </div>
  )
}