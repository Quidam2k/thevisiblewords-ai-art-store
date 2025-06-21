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
      title: 'Whimsical Forest Dreams',
      description: 'A magical forest scene with floating lights and mystical creatures',
      prompt: 'magical forest with glowing orbs, fairy lights, whimsical creatures, dreamy atmosphere',
      fileUrl: '/images/sample/whimsical-forest.jpg',
      thumbnailUrl: '/images/sample/whimsical-forest-thumb.jpg',
      tags: ['fantasy', 'forest', 'magical', 'whimsical', 'nature'],
      style: 'WHIMSY' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#4A90E2', '#50C878', '#FFD700', '#DDA0DD'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 2048000,
        recommendedProducts: [
          { printifyBlueprintId: 3, confidence: 0.9, reason: 'Great for apparel', variants: [1, 2, 3], category: 'Apparel', name: 'T-Shirt' },
          { printifyBlueprintId: 384, confidence: 0.85, reason: 'Perfect for wall art', variants: [1, 2], category: 'Wall Art', name: 'Poster' }
        ]
      }
    },
    {
      title: 'Epic Dragon Mountain',
      description: 'A massive dragon soaring over snow-capped mountains with dramatic lighting',
      prompt: 'epic dragon flying over mountains, dramatic sky, fantasy landscape, powerful and majestic',
      fileUrl: '/images/sample/epic-dragon.jpg',
      thumbnailUrl: '/images/sample/epic-dragon-thumb.jpg',
      tags: ['dragon', 'epic', 'mountains', 'fantasy', 'dramatic'],
      style: 'EPIC' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#8B0000', '#2F4F4F', '#FFD700', '#000000'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 2156000,
        recommendedProducts: [
          { printifyBlueprintId: 384, confidence: 0.95, reason: 'Epic scenes work great as posters', variants: [1, 2, 3], category: 'Wall Art', name: 'Poster' },
          { printifyBlueprintId: 480, confidence: 0.9, reason: 'Dramatic for canvas prints', variants: [1, 2], category: 'Wall Art', name: 'Canvas' }
        ]
      }
    },
    {
      title: 'Hybrid Cyber Garden',
      description: 'A futuristic garden where technology and nature blend seamlessly',
      prompt: 'cyberpunk garden, neon plants, technology meets nature, hybrid aesthetic, colorful and mysterious',
      fileUrl: '/images/sample/hybrid-cyber.jpg',
      thumbnailUrl: '/images/sample/hybrid-cyber-thumb.jpg',
      tags: ['cyberpunk', 'nature', 'technology', 'futuristic', 'neon'],
      style: 'HYBRID' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#00FFFF', '#FF1493', '#32CD32', '#9400D3'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 1987000,
        recommendedProducts: [
          { printifyBlueprintId: 3, confidence: 0.8, reason: 'Cool design for apparel', variants: [1, 2, 3], category: 'Apparel', name: 'T-Shirt' },
          { printifyBlueprintId: 32, confidence: 0.85, reason: 'Unique design for phone cases', variants: [1], category: 'Accessories', name: 'Phone Case' }
        ]
      }
    },
    {
      title: 'Peaceful Zen Garden',
      description: 'A serene Japanese garden with cherry blossoms and meditation stones',
      prompt: 'zen garden, cherry blossoms, peaceful meditation space, soft colors, tranquil atmosphere',
      fileUrl: '/images/sample/zen-garden.jpg',
      thumbnailUrl: '/images/sample/zen-garden-thumb.jpg',
      tags: ['zen', 'peaceful', 'japanese', 'meditation', 'flowers'],
      style: 'WHIMSY' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#FFB6C1', '#98FB98', '#F0E68C', '#E6E6FA'],
        complexity: 'medium' as const,
        quality: 'high' as const,
        fileSize: 1756000,
        recommendedProducts: [
          { printifyBlueprintId: 5, confidence: 0.9, reason: 'Peaceful designs work well on mugs', variants: [1], category: 'Home & Living', name: 'Mug' },
          { printifyBlueprintId: 384, confidence: 0.8, reason: 'Calming art for wall display', variants: [1, 2], category: 'Wall Art', name: 'Poster' }
        ]
      }
    },
    {
      title: 'Epic Space Battle',
      description: 'Massive spaceships engaged in an intense battle among the stars',
      prompt: 'epic space battle, massive spaceships, lasers, stars, dramatic sci-fi scene',
      fileUrl: '/images/sample/space-battle.jpg',
      thumbnailUrl: '/images/sample/space-battle-thumb.jpg',
      tags: ['space', 'battle', 'sci-fi', 'spaceships', 'epic'],
      style: 'EPIC' as const,
      analysis: {
        dimensions: { width: 2048, height: 2048, aspectRatio: 1 },
        hasAlpha: false,
        dominantColors: ['#000080', '#FF4500', '#FFFFFF', '#FFD700'],
        complexity: 'high' as const,
        quality: 'high' as const,
        fileSize: 2234000,
        recommendedProducts: [
          { printifyBlueprintId: 384, confidence: 0.95, reason: 'Epic space scenes are perfect for posters', variants: [1, 2, 3], category: 'Wall Art', name: 'Poster' },
          { printifyBlueprintId: 3, confidence: 0.8, reason: 'Cool sci-fi design for apparel', variants: [1, 2], category: 'Apparel', name: 'T-Shirt' }
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
            images: [artwork.fileUrl], // Use artwork image as product image
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