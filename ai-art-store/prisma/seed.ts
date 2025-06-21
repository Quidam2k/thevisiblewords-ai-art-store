import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Starting database seed...')

  // Create sample artworks
  const artworks = await createSampleArtworks()
  console.log(`✅ Created ${artworks.length} sample artworks`)

  // Create sample products for each artwork
  const products = await createSampleProducts(artworks)
  console.log(`✅ Created ${products.length} sample products`)

  // Create sample admin user
  const adminUser = await createAdminUser()
  console.log(`✅ Created admin user: ${adminUser.email}`)

  console.log('🎉 Database seeding completed!')
}

async function createSampleArtworks() {
  const sampleArtworks = [
    {
      title: 'Luminous Meadow Pavilion',
      description: 'Ethereal architectural structure suspended in a twilight meadow with glowing paper lanterns creating magical ambiance',
      prompt: 'A pop-up shop on a meadow futuristic art architecture with paper lanterns, twilight lighting, ethereal atmosphere',
      fileUrl: '/sample-product-1.png',
      thumbnailUrl: '/sample-product-1.png',
      tags: JSON.stringify(['architecture', 'meadow', 'lanterns', 'twilight', 'ethereal', 'peaceful', 'zen']),
      style: 'WHIMSY' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#FF8C42', '#4A90E2', '#2F4F4F', '#F4A460'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 2048000,
        recommendedProducts: [
          { printifyBlueprintId: 384, confidence: 0.95, reason: 'Atmospheric scenes perfect for wall art', variants: [1, 2, 3], category: 'Wall Art', name: 'Poster' },
          { printifyBlueprintId: 3, confidence: 0.8, reason: 'Peaceful design great for apparel', variants: [1, 2, 3], category: 'Apparel', name: 'T-Shirt' }
        ]
      }
    },
    {
      title: 'Sacred Stained Glass Angels',
      description: 'Dramatic stained glass artwork featuring opposing angels in brilliant red and blue with intricate geometric patterns',
      prompt: 'stained glass angels, red and blue contrast, sacred art, geometric patterns, dramatic lighting, spiritual battle',
      fileUrl: '/sample-product-2.png',
      thumbnailUrl: '/sample-product-2.png',
      tags: JSON.stringify(['stained-glass', 'angels', 'religious', 'geometric', 'dramatic', 'spiritual', 'contrast']),
      style: 'EPIC' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#DC143C', '#4169E1', '#FFD700', '#FFFFFF'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 2156000,
        recommendedProducts: [
          { printifyBlueprintId: 384, confidence: 0.98, reason: 'Stained glass designs are perfect for poster art', variants: [1, 2, 3], category: 'Wall Art', name: 'Poster' },
          { printifyBlueprintId: 480, confidence: 0.95, reason: 'Spiritual art works beautifully on canvas', variants: [1, 2], category: 'Wall Art', name: 'Canvas' }
        ]
      }
    },
    {
      title: 'Enchanted Library Sanctuary',
      description: 'Mystical ancient library with towering bookshelves, natural overgrowth, and ethereal lighting through gothic windows',
      prompt: 'fantasy magic library with books, overgrown plants, gothic windows, mystical atmosphere, ancient knowledge',
      fileUrl: '/sample-product-3.png',
      thumbnailUrl: '/sample-product-3.png',
      tags: JSON.stringify(['library', 'fantasy', 'books', 'gothic', 'mystical', 'ancient', 'magical']),
      style: 'HYBRID' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#2F4F4F', '#228B22', '#DAA520', '#F5DEB3'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 1987000,
        recommendedProducts: [
          { printifyBlueprintId: 384, confidence: 0.9, reason: 'Literary themes work excellently as wall art', variants: [1, 2, 3], category: 'Wall Art', name: 'Poster' },
          { printifyBlueprintId: 5, confidence: 0.85, reason: 'Book lovers would love this on a mug', variants: [1], category: 'Home & Living', name: 'Mug' },
          { printifyBlueprintId: 3, confidence: 0.8, reason: 'Fantasy design appeals to broad apparel market', variants: [1, 2], category: 'Apparel', name: 'T-Shirt' }
        ]
      }
    }
  ]

  const createdArtworks = []
  for (const artwork of sampleArtworks) {
    const created = await prisma.artwork.create({
      data: artwork
    })
    createdArtworks.push(created)
  }

  return createdArtworks
}

async function createSampleProducts(artworks: any[]) {
  const createdProducts = []

  for (const artwork of artworks) {
    // Create multiple product variants for each artwork
    const productTemplates = [
      {
        category: 'Apparel',
        printifyBlueprintId: 3, // T-shirt
        printProviderId: 1,
        basePrice: 2499, // $24.99
        variants: [
          { id: 1, price: 2499, title: 'S / White', options: { size: 'S', color: 'White' }, available: true },
          { id: 2, price: 2499, title: 'M / White', options: { size: 'M', color: 'White' }, available: true },
          { id: 3, price: 2499, title: 'L / White', options: { size: 'L', color: 'White' }, available: true },
          { id: 4, price: 2499, title: 'S / Black', options: { size: 'S', color: 'Black' }, available: true },
          { id: 5, price: 2499, title: 'M / Black', options: { size: 'M', color: 'Black' }, available: true },
          { id: 6, price: 2499, title: 'L / Black', options: { size: 'L', color: 'Black' }, available: true },
        ]
      },
      {
        category: 'Wall Art',
        printifyBlueprintId: 384, // Poster
        printProviderId: 1,
        basePrice: 1999, // $19.99
        variants: [
          { id: 1, price: 1999, title: '12" x 12"', options: { size: '12x12' }, available: true },
          { id: 2, price: 2999, title: '16" x 16"', options: { size: '16x16' }, available: true },
          { id: 3, price: 3999, title: '20" x 20"', options: { size: '20x20' }, available: true },
        ]
      }
    ]

    // Create products only for recommended blueprints
    const recommendations = artwork.analysis?.recommendedProducts || []
    
    for (const template of productTemplates) {
      const isRecommended = recommendations.some(
        (rec: any) => rec.printifyBlueprintId === template.printifyBlueprintId
      )

      if (isRecommended || recommendations.length === 0) {
        const product = await prisma.product.create({
          data: {
            artworkId: artwork.id,
            title: `${artwork.title} - ${template.category}`,
            description: `${artwork.description} Available as premium ${template.category.toLowerCase()}.`,
            basePrice: template.basePrice,
            printifyBlueprintId: template.printifyBlueprintId,
            printProviderId: template.printProviderId,
            variants: template.variants,
            images: JSON.stringify([artwork.fileUrl]), // Use artwork image as product image
            category: template.category,
            featured: Math.random() > 0.7, // Randomly feature some products
            active: true,
          }
        })
        createdProducts.push(product)
      }
    }
  }

  return createdProducts
}

async function createAdminUser() {
  // Create a sample admin user
  const adminUser = await prisma.adminUser.create({
    data: {
      email: 'admin@thevisiblewords.com',
      name: 'Admin User',
      passwordHash: 'placeholder_hash', // In real app, hash the password
      role: 'SUPER_ADMIN',
      active: true,
    }
  })

  return adminUser
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })