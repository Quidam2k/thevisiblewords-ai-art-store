import { Hero } from '@/components/sections/hero'
import { FeaturedProducts } from '@/components/sections/featured-products'
import { StyleShowcase } from '@/components/sections/style-showcase'
import { CustomRequestSection } from '@/components/sections/custom-request'
import { Newsletter } from '@/components/sections/newsletter'

export default function HomePage() {
  return (
    <div className="space-y-16">
      <Hero />
      <FeaturedProducts />
      <StyleShowcase />
      <CustomRequestSection />
      <Newsletter />
    </div>
  )
}