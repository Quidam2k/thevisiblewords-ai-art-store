import { NextRequest, NextResponse } from 'next/server'
import { createCheckoutSession } from '@/lib/stripe'
import { CheckoutData } from '@/types'

export async function POST(request: NextRequest) {
  try {
    const checkoutData: CheckoutData = await request.json()

    // Validate required fields
    if (!checkoutData.customerEmail || !checkoutData.cartItems || checkoutData.cartItems.length === 0) {
      return NextResponse.json(
        { error: 'Missing required checkout data' },
        { status: 400 }
      )
    }

    // Create Stripe checkout session
    const result = await createCheckoutSession(
      checkoutData,
      `${process.env.NEXT_PUBLIC_BASE_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      `${process.env.NEXT_PUBLIC_BASE_URL}/checkout/cancel`
    )

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Failed to create checkout session' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      sessionId: result.sessionId,
      url: result.url,
    })
  } catch (error) {
    console.error('Checkout error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}