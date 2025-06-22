import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { printifyAPI } from '@/lib/printify'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params

    // Fetch product from database with artwork data
    const product = await db.product.findUnique({
      where: { id },
      include: {
        artwork: true
      }
    })

    if (!product) {
      return NextResponse.json(
        { error: 'Product not found' },
        { status: 404 }
      )
    }

    // If we have a Printify product ID, fetch live data for freshness
    let liveProductData = null
    if (product.printifyProductId) {
      try {
        const printifyResponse = await printifyAPI.getProduct(product.printifyProductId)
        if (printifyResponse.success) {
          liveProductData = printifyResponse.data
        }
      } catch (error) {
        console.warn('Failed to fetch live Printify data:', error)
        // Continue with database data
      }
    }

    // Merge database data with live Printify data if available
    const productData = {
      ...product,
      // Use live data if available, otherwise fall back to database
      variants: liveProductData?.variants || product.variants,
      images: liveProductData?.images?.map((img: any) => img.src) || product.images,
      printifyData: liveProductData,
    }

    // Fetch related products (same style or category)
    const relatedProducts = await db.product.findMany({
      where: {
        AND: [
          { id: { not: product.id } }, // Exclude current product
          { active: true },
          {
            OR: [
              { category: product.category },
              { artwork: { style: product.artwork.style } }
            ]
          }
        ]
      },
      include: {
        artwork: true
      },
      take: 4,
      orderBy: {
        createdAt: 'desc'
      }
    })

    return NextResponse.json({
      product: productData,
      relatedProducts
    })

  } catch (error) {
    console.error('Error fetching product:', error)
    return NextResponse.json(
      { error: 'Failed to fetch product' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const updateData = await request.json()

    // TODO: Add authentication check for admin users

    const product = await db.product.update({
      where: { id },
      data: {
        ...updateData,
        updatedAt: new Date()
      },
      include: {
        artwork: true
      }
    })

    return NextResponse.json(product)

  } catch (error) {
    console.error('Error updating product:', error)
    return NextResponse.json(
      { error: 'Failed to update product' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params

    // TODO: Add authentication check for admin users

    // Soft delete by setting active to false
    const product = await db.product.update({
      where: { id },
      data: {
        active: false,
        updatedAt: new Date()
      }
    })

    return NextResponse.json({ 
      message: 'Product deactivated successfully',
      product 
    })

  } catch (error) {
    console.error('Error deleting product:', error)
    return NextResponse.json(
      { error: 'Failed to delete product' },
      { status: 500 }
    )
  }
}