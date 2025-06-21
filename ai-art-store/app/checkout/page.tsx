'use client'

import { useState } from 'react'
import { useCart } from '@/hooks/use-cart'
import { CheckoutForm } from '@/components/checkout/checkout-form'
import { OrderSummary } from '@/components/checkout/order-summary'
import { useRouter } from 'next/navigation'

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart()
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  // Redirect if cart is empty
  if (items.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Your cart is empty</h1>
          <p className="text-gray-600 mb-8">Add some products before checking out.</p>
          <button
            onClick={() => router.push('/shop')}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    )
  }

  const handleCheckout = async (formData: any) => {
    setLoading(true)
    
    try {
      const checkoutData = {
        customerEmail: formData.email,
        customerName: `${formData.firstName} ${formData.lastName}`,
        customerPhone: formData.phone,
        shippingAddress: {
          firstName: formData.firstName,
          lastName: formData.lastName,
          company: formData.company,
          address1: formData.address1,
          address2: formData.address2,
          city: formData.city,
          state: formData.state,
          country: formData.country,
          zip: formData.zip,
        },
        cartItems: items,
      }

      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(checkoutData),
      })

      const result = await response.json()

      if (result.url) {
        // Redirect to Stripe Checkout
        window.location.href = result.url
      } else {
        throw new Error(result.error || 'Failed to create checkout session')
      }
    } catch (error) {
      console.error('Checkout error:', error)
      alert('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <CheckoutForm onSubmit={handleCheckout} loading={loading} />
        </div>
        
        <div>
          <OrderSummary items={items} total={total} />
        </div>
      </div>
    </div>
  )
}