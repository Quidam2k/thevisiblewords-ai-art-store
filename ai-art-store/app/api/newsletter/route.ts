import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { validateEmail } from '@/lib/utils'

export async function POST(request: NextRequest) {
  try {
    const { email, name, source } = await request.json()

    if (!email || !validateEmail(email)) {
      return NextResponse.json(
        { error: 'Valid email is required' },
        { status: 400 }
      )
    }

    // Check if email already exists
    const existing = await db.newsletter.findUnique({
      where: { email },
    })

    if (existing) {
      if (existing.active) {
        return NextResponse.json(
          { message: 'Email already subscribed' },
          { status: 200 }
        )
      } else {
        // Reactivate subscription
        await db.newsletter.update({
          where: { email },
          data: { active: true },
        })
        return NextResponse.json({
          message: 'Subscription reactivated successfully',
        })
      }
    }

    // Create new subscription
    await db.newsletter.create({
      data: {
        email,
        name: name || null,
        source: source || 'unknown',
        active: true,
      },
    })

    return NextResponse.json({
      message: 'Successfully subscribed to newsletter',
    })
  } catch (error) {
    console.error('Newsletter subscription error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}