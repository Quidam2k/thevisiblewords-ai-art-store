import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { printifyAPI } from '@/lib/printify'
import { ProductFilters } from '@/types'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Parse query parameters
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '12')
    const category = searchParams.get('category')
    const style = searchParams.get('style')
    const search = searchParams.get('search')
    const sortBy = searchParams.get('sortBy') || 'newest'
    const minPrice = searchParams.get('minPrice') ? parseInt(searchParams.get('minPrice')!) : undefined
    const maxPrice = searchParams.get('maxPrice') ? parseInt(searchParams.get('maxPrice')!) : undefined

    // Build where clause for filtering
    const where: any = {
      active: true,
    }

    // Add filters
    if (category) {
      where.category = category
    }

    if (style && style !== 'all') {
      where.artwork = {
        style: style.toUpperCase()
      }
    }

    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } },
        { artwork: { tags: { hasSome: [search] } } }
      ]
    }

    if (minPrice || maxPrice) {
      where.basePrice = {}
      if (minPrice) where.basePrice.gte = minPrice
      if (maxPrice) where.basePrice.lte = maxPrice
    }

    // Build orderBy clause
    let orderBy: any = { createdAt: 'desc' } // default: newest first
    
    switch (sortBy) {
      case 'price-low':
        orderBy = { basePrice: 'asc' }
        break
      case 'price-high':
        orderBy = { basePrice: 'desc' }
        break
      case 'popular':
        // TODO: Add popularity field based on sales
        orderBy = { featured: 'desc' }
        break
      case 'newest':
      default:
        orderBy = { createdAt: 'desc' }
        break
    }

    // Calculate offset for pagination
    const offset = (page - 1) * limit

    // Fetch products with artwork data
    const [products, totalCount] = await Promise.all([
      db.product.findMany({
        where,
        include: {
          artwork: true
        },
        orderBy,
        skip: offset,
        take: limit,
      }),
      db.product.count({ where })
    ])

    // Calculate pagination info
    const totalPages = Math.ceil(totalCount / limit)
    const hasNext = page < totalPages
    const hasPrev = page > 1

    return NextResponse.json({
      products,
      pagination: {
        page,
        limit,
        total: totalCount,
        totalPages,
        hasNext,
        hasPrev,
      },
      filters: {
        category,
        style,
        search,
        sortBy,
        minPrice,
        maxPrice,
      }
    })

  } catch (error) {
    console.error('Error fetching products:', error)
    return NextResponse.json(
      { error: 'Failed to fetch products' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action } = body

    if (action === 'sync') {
      // Sync products from Printify
      const syncResult = await syncProductsFromPrintify()
      return NextResponse.json(syncResult)
    }

    // Create new product (admin only)
    // TODO: Add authentication check
    const productData = body
    
    const product = await db.product.create({
      data: {
        ...productData,
        active: true,
      },
      include: {
        artwork: true
      }
    })

    return NextResponse.json(product)

  } catch (error) {
    console.error('Error creating/syncing products:', error)
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    )
  }
}

// Sync products from Printify to local database
async function syncProductsFromPrintify() {
  try {
    console.log('Starting Printify product sync...')
    
    // Fetch all products from Printify
    const printifyResponse = await printifyAPI.getProducts(1, 100) // Get up to 100 products
    
    if (!printifyResponse.success) {
      throw new Error(printifyResponse.error || 'Failed to fetch from Printify')
    }

    const printifyProducts = printifyResponse.data?.data || []
    console.log(`Found ${printifyProducts.length} products in Printify`)

    let syncedCount = 0
    let errorCount = 0
    const errors: string[] = []

    for (const printifyProduct of printifyProducts) {
      try {
        // Check if product already exists in our database
        const existingProduct = await db.product.findUnique({
          where: { printifyProductId: printifyProduct.id }
        })

        if (existingProduct) {
          // Update existing product
          await db.product.update({
            where: { id: existingProduct.id },
            data: {
              title: printifyProduct.title,
              description: printifyProduct.description,
              variants: printifyProduct.variants,
              images: printifyProduct.images.map((img: any) => img.src),
              active: printifyProduct.visible,
              updatedAt: new Date(),
            }
          })
          console.log(`Updated product: ${printifyProduct.title}`)
        } else {
          // Create new product entry
          // Note: We'll need to create artwork entries separately or link to existing ones
          console.log(`New product found: ${printifyProduct.title}`)
          console.log('Skipping creation - needs artwork association')
          // TODO: Implement logic to associate with existing artwork or create new artwork
        }

        syncedCount++

      } catch (productError) {
        console.error(`Error syncing product ${printifyProduct.id}:`, productError)
        errorCount++
        errors.push(`Product ${printifyProduct.title}: ${productError}`)
      }
    }

    const result = {
      success: true,
      message: `Sync completed: ${syncedCount} products processed, ${errorCount} errors`,
      syncedCount,
      errorCount,
      errors: errors.slice(0, 5), // Return first 5 errors
      timestamp: new Date().toISOString()
    }

    console.log('Printify sync completed:', result)
    return result

  } catch (error) {
    console.error('Printify sync failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown sync error',
      timestamp: new Date().toISOString()
    }
  }
}