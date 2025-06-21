import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET(request: NextRequest) {
  try {
    // Get unique categories from products
    const categories = await db.product.findMany({
      where: { 
        active: true,
        category: { not: null }
      },
      select: { 
        category: true 
      },
      distinct: ['category']
    })

    // Get unique styles from artwork
    const styles = await db.artwork.findMany({
      where: { 
        active: true,
        products: {
          some: {
            active: true
          }
        }
      },
      select: { 
        style: true 
      },
      distinct: ['style']
    })

    // Get product counts for each category
    const categoryStats = await Promise.all(
      categories.map(async (cat) => {
        if (!cat.category) return null
        
        const count = await db.product.count({
          where: {
            active: true,
            category: cat.category
          }
        })
        
        return {
          name: cat.category,
          slug: cat.category.toLowerCase().replace(/\s+/g, '-'),
          count
        }
      })
    )

    // Get product counts for each style
    const styleStats = await Promise.all(
      styles.map(async (style) => {
        const count = await db.product.count({
          where: {
            active: true,
            artwork: {
              style: style.style
            }
          }
        })
        
        return {
          name: style.style,
          slug: style.style.toLowerCase(),
          count
        }
      })
    )

    // Get price range
    const priceRange = await db.product.aggregate({
      where: { active: true },
      _min: { basePrice: true },
      _max: { basePrice: true }
    })

    // Get popular tags
    const artworks = await db.artwork.findMany({
      where: {
        active: true,
        products: {
          some: {
            active: true
          }
        }
      },
      select: { tags: true }
    })

    // Flatten and count tags
    const tagCounts = artworks
      .flatMap(artwork => artwork.tags)
      .reduce((acc, tag) => {
        acc[tag] = (acc[tag] || 0) + 1
        return acc
      }, {} as Record<string, number>)

    // Get top 20 tags
    const popularTags = Object.entries(tagCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 20)
      .map(([tag, count]) => ({ tag, count }))

    return NextResponse.json({
      categories: categoryStats.filter(Boolean),
      styles: styleStats,
      priceRange: {
        min: priceRange._min.basePrice || 0,
        max: priceRange._max.basePrice || 10000
      },
      popularTags,
      totalProducts: await db.product.count({ where: { active: true } })
    })

  } catch (error) {
    console.error('Error fetching categories:', error)
    return NextResponse.json(
      { error: 'Failed to fetch categories' },
      { status: 500 }
    )
  }
}