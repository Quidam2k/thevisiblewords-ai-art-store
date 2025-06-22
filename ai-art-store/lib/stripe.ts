// Stripe payment processing
import Stripe from 'stripe'
import { CheckoutData, CartItem } from '@/types'

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY is required')
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-06-20',
})

// Create checkout session
export async function createCheckoutSession(
  checkoutData: CheckoutData,
  successUrl: string,
  cancelUrl: string
) {
  try {
    const lineItems = checkoutData.cartItems.map((item: CartItem) => ({
      price_data: {
        currency: 'usd',
        product_data: {
          name: item.title,
          images: [item.image],
          metadata: {
            product_id: item.productId,
            variant_id: item.variant.id.toString(),
            artwork_style: item.artworkStyle,
          },
        },
        unit_amount: item.price, // Stripe expects amount in cents
      },
      quantity: item.quantity,
    }))

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: lineItems,
      mode: 'payment',
      success_url: successUrl,
      cancel_url: cancelUrl,
      customer_email: checkoutData.customerEmail,
      shipping_address_collection: {
        allowed_countries: ['US', 'CA'], // Add more countries as needed
      },
      phone_number_collection: {
        enabled: true,
      },
      metadata: {
        customer_name: checkoutData.customerName,
        order_data: JSON.stringify({
          cartItems: checkoutData.cartItems,
          customerInfo: {
            email: checkoutData.customerEmail,
            name: checkoutData.customerName,
            phone: checkoutData.customerPhone,
          },
        }),
      },
      allow_promotion_codes: true,
    })

    return { success: true, sessionId: session.id, url: session.url }
  } catch (error) {
    console.error('Stripe checkout session error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create checkout session',
    }
  }
}

// Retrieve checkout session
export async function retrieveCheckoutSession(sessionId: string) {
  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId, {
      expand: ['line_items', 'customer_details'],
    })
    return { success: true, session }
  } catch (error) {
    console.error('Error retrieving checkout session:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to retrieve session',
    }
  }
}

// Create payment intent for custom checkout
export async function createPaymentIntent(
  amount: number,
  metadata: Record<string, string> = {}
) {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: 'usd',
      metadata,
      automatic_payment_methods: {
        enabled: true,
      },
    })

    return {
      success: true,
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    }
  } catch (error) {
    console.error('Error creating payment intent:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create payment intent',
    }
  }
}

// Verify webhook signature
export function verifyWebhookSignature(
  payload: string | Buffer,
  signature: string,
  secret: string
): Stripe.Event | null {
  try {
    return stripe.webhooks.constructEvent(payload, signature, secret)
  } catch (error) {
    console.error('Webhook signature verification failed:', error)
    return null
  }
}

// Refund payment
export async function refundPayment(
  paymentIntentId: string,
  amount?: number,
  reason?: string
) {
  try {
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId,
      amount,
      reason,
    })

    return { success: true, refund }
  } catch (error) {
    console.error('Error creating refund:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create refund',
    }
  }
}

// Calculate tax (simplified - integrate with real tax service as needed)
export function calculateTax(subtotal: number, state: string): number {
  // Simplified tax calculation - replace with real tax service
  const taxRates: Record<string, number> = {
    CA: 0.0875, // California
    NY: 0.08,   // New York
    TX: 0.0625, // Texas
    FL: 0.06,   // Florida
    // Add more states as needed
  }

  const taxRate = taxRates[state] || 0
  return Math.round(subtotal * taxRate)
}

// Calculate shipping (simplified - integrate with real shipping service)
export function calculateShipping(
  items: CartItem[],
  shippingAddress: any
): number {
  // Simplified shipping calculation - replace with real shipping service
  const baseShipping = 599 // $5.99 base shipping
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0)
  
  // Free shipping over $75
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  if (subtotal >= 7500) return 0
  
  // Additional cost for multiple items
  const additionalCost = Math.max(0, (itemCount - 1) * 200) // $2 per additional item
  
  return baseShipping + additionalCost
}

export default stripe