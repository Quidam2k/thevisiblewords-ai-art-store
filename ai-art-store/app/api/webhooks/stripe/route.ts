import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'
import { verifyWebhookSignature } from '@/lib/stripe'
import { db } from '@/lib/db'
import { printifyAPI } from '@/lib/printify'

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const signature = headers().get('stripe-signature')

    if (!signature) {
      return NextResponse.json(
        { error: 'Missing Stripe signature' },
        { status: 400 }
      )
    }

    const event = verifyWebhookSignature(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )

    if (!event) {
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 400 }
      )
    }

    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object)
        break
      
      case 'payment_intent.succeeded':
        await handlePaymentSucceeded(event.data.object)
        break
      
      case 'payment_intent.payment_failed':
        await handlePaymentFailed(event.data.object)
        break

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return NextResponse.json({ received: true })
  } catch (error) {
    console.error('Webhook error:', error)
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    )
  }
}

async function handleCheckoutCompleted(session: any) {
  try {
    // Parse order data from session metadata
    const orderData = JSON.parse(session.metadata.order_data)
    
    // Create order in database
    const order = await db.order.create({
      data: {
        stripePaymentIntentId: session.payment_intent,
        customerEmail: session.customer_details.email,
        customerName: orderData.customerInfo.name,
        customerPhone: orderData.customerInfo.phone,
        shippingAddress: session.shipping_details?.address || session.customer_details?.address,
        totalAmount: session.amount_total,
        subtotal: session.amount_subtotal,
        tax: session.total_details?.amount_tax || 0,
        shipping: session.total_details?.amount_shipping || 0,
        status: 'PAID',
        orderItems: {
          create: orderData.cartItems.map((item: any) => ({
            productId: item.productId,
            printifyVariantId: item.variant.id,
            quantity: item.quantity,
            unitPrice: item.price,
            totalPrice: item.price * item.quantity,
            productSnapshot: item,
          })),
        },
      },
      include: {
        orderItems: {
          include: {
            product: true,
          },
        },
      },
    })

    // Submit order to Printify
    await submitOrderToPrintify(order)

    console.log(`Order ${order.id} created and submitted to Printify`)
  } catch (error) {
    console.error('Error handling checkout completed:', error)
  }
}

async function handlePaymentSucceeded(paymentIntent: any) {
  try {
    // Update order status
    await db.order.updateMany({
      where: { stripePaymentIntentId: paymentIntent.id },
      data: { status: 'PROCESSING' },
    })

    console.log(`Payment succeeded for order: ${paymentIntent.id}`)
  } catch (error) {
    console.error('Error handling payment succeeded:', error)
  }
}

async function handlePaymentFailed(paymentIntent: any) {
  try {
    // Update order status
    await db.order.updateMany({
      where: { stripePaymentIntentId: paymentIntent.id },
      data: { status: 'CANCELLED' },
    })

    console.log(`Payment failed for order: ${paymentIntent.id}`)
  } catch (error) {
    console.error('Error handling payment failed:', error)
  }
}

async function submitOrderToPrintify(order: any) {
  try {
    const printifyOrder = {
      external_id: order.id,
      line_items: order.orderItems.map((item: any) => ({
        product_id: item.product.printifyProductId,
        variant_id: item.printifyVariantId,
        quantity: item.quantity,
      })),
      shipping_method: 1, // Standard shipping
      send_shipping_notification: true,
      address_to: {
        first_name: order.shippingAddress.first_name || order.customerName?.split(' ')[0] || '',
        last_name: order.shippingAddress.last_name || order.customerName?.split(' ').slice(1).join(' ') || '',
        email: order.customerEmail,
        phone: order.customerPhone || '',
        country: order.shippingAddress.country || 'US',
        region: order.shippingAddress.state || order.shippingAddress.region || '',
        address1: order.shippingAddress.line1 || order.shippingAddress.address1 || '',
        address2: order.shippingAddress.line2 || order.shippingAddress.address2 || '',
        city: order.shippingAddress.city || '',
        zip: order.shippingAddress.postal_code || order.shippingAddress.zip || '',
      },
    }

    const result = await printifyAPI.submitOrder(printifyOrder)

    if (result.success) {
      // Update order with Printify order ID
      await db.order.update({
        where: { id: order.id },
        data: {
          printifyOrderId: result.data.id,
          status: 'PROCESSING',
        },
      })
    } else {
      console.error('Failed to submit order to Printify:', result.error)
      // Keep order in PAID status for manual review
    }
  } catch (error) {
    console.error('Error submitting order to Printify:', error)
  }
}