import { NextRequest, NextResponse } from 'next/server'
import { printifyAPI } from '@/lib/printify'
import { db } from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    // TODO: Add admin authentication check
    // if (!isAdmin(request)) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // }

    const { action, productId } = await request.json()

    switch (action) {
      case 'sync-all':
        return await syncAllProducts()
      case 'sync-single':
        return await syncSingleProduct(productId)
      case 'create-sample':
        return await createSampleProducts()
      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }

  } catch (error) {
    console.error('Admin sync error:', error)
    return NextResponse.json(
      { error: 'Sync operation failed' },
      { status: 500 }
    )
  }
}

async function syncAllProducts() {
  console.log('Starting full Printify sync...')
  
  try {
    // Fetch all products from Printify
    let allProducts: any[] = []
    let page = 1
    let hasMore = true

    while (hasMore && page <= 10) { // Limit to 10 pages for safety
      const response = await printifyAPI.getProducts(page, 50)
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch from Printify')
      }

      const products = response.data?.data || []
      allProducts.push(...products)
      
      // Check if there are more pages
      hasMore = products.length === 50
      page++
    }

    console.log(`Found ${allProducts.length} total products in Printify`)

    let syncedCount = 0
    let createdCount = 0
    let updatedCount = 0
    let errorCount = 0
    const errors: string[] = []

    for (const printifyProduct of allProducts) {
      try {
        await syncProductFromPrintify(printifyProduct)
        syncedCount++
        
        // Check if product was created or updated
        const existingProduct = await db.product.findUnique({
          where: { printifyProductId: printifyProduct.id }
        })
        
        if (existingProduct) {
          updatedCount++
        } else {
          createdCount++
        }

      } catch (error) {
        console.error(`Error syncing product ${printifyProduct.id}:`, error)
        errorCount++
        errors.push(`${printifyProduct.title}: ${error}`)
      }
    }

    return NextResponse.json({
      success: true,
      message: `Sync completed: ${syncedCount} products processed`,
      stats: {
        total: allProducts.length,
        synced: syncedCount,
        created: createdCount,
        updated: updatedCount,
        errors: errorCount
      },
      errors: errors.slice(0, 10), // Return first 10 errors
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Full sync failed:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown sync error'
    }, { status: 500 })
  }
}

async function syncSingleProduct(printifyProductId: string) {
  try {
    // Fetch single product from Printify
    const response = await printifyAPI.getProduct(printifyProductId)
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to fetch product from Printify')
    }

    await syncProductFromPrintify(response.data)

    return NextResponse.json({
      success: true,
      message: `Product ${printifyProductId} synced successfully`
    })

  } catch (error) {
    console.error('Single product sync failed:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown sync error'
    }, { status: 500 })
  }
}

async function syncProductFromPrintify(printifyProduct: any) {
  // Check if product already exists
  const existingProduct = await db.product.findUnique({
    where: { printifyProductId: printifyProduct.id }
  })

  // Calculate base price (using first variant or average)
  const variants = printifyProduct.variants || []
  let basePrice = 2500 // Default $25.00
  
  if (variants.length > 0) {
    // Use the price of the first variant with markup
    const firstVariantPrice = variants[0].price || 1000
    basePrice = Math.round(firstVariantPrice * 2.5) // 150% markup
  }

  // Extract main product image
  const images = printifyProduct.images || []
  const productImages = images.map((img: any) => img.src).filter(Boolean)

  // Determine category based on blueprint_id
  const category = getCategoryFromBlueprint(printifyProduct.blueprint_id)

  const productData = {
    printifyProductId: printifyProduct.id,
    title: printifyProduct.title || 'Untitled Product',
    description: printifyProduct.description || '',
    basePrice,
    printifyBlueprintId: printifyProduct.blueprint_id,
    printProviderId: printifyProduct.print_provider_id,
    variants: printifyProduct.variants,
    images: productImages,
    category,
    active: printifyProduct.visible || false,
    featured: false,
  }

  if (existingProduct) {
    // Update existing product
    await db.product.update({
      where: { id: existingProduct.id },
      data: {
        ...productData,
        updatedAt: new Date()
      }
    })
    console.log(`Updated product: ${printifyProduct.title}`)
  } else {
    // Need to associate with artwork
    // For now, we'll create a placeholder artwork or skip
    console.log(`New product found: ${printifyProduct.title}`)
    console.log('Skipping - needs artwork association')
    
    // TODO: Implement artwork association logic
    // This could involve:
    // 1. Matching by title/description
    // 2. Creating placeholder artwork
    // 3. Manual admin association
  }
}

function getCategoryFromBlueprint(blueprintId: number): string {
  // Map Printify blueprint IDs to categories
  const blueprintCategories: Record<number, string> = {
    3: 'Apparel',      // T-shirt
    6: 'Apparel',      // Hoodie
    9: 'Apparel',      // Tank Top
    384: 'Wall Art',   // Poster
    480: 'Wall Art',   // Canvas
    5: 'Home & Living', // Mug
    26: 'Accessories', // Tote Bag
    32: 'Accessories', // Phone Case
    // Add more mappings as needed
  }

  return blueprintCategories[blueprintId] || 'Other'
}

async function createSampleProducts() {
  try {
    console.log('Creating sample products...')
    
    // This would integrate with your existing automation
    // For now, return a placeholder response
    
    return NextResponse.json({
      success: true,
      message: 'Sample product creation is ready for integration with existing automation',
      note: 'Connect this to your printify_automation_script_Copy/ system'
    })

  } catch (error) {
    console.error('Sample product creation failed:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}