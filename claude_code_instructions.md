# Claude Code Quick Start Instructions

## Immediate Action Items

### 1. First, Run Site Analysis
```bash
# Clone/download the Playwright analysis script
# Install Playwright if not already installed
npm init -y
npm install @playwright/test
npx playwright install

# Run the analysis script to capture current site
npx playwright test playwright-analysis.ts --headed

# This will generate:
# - Screenshots of current site
# - Product data extraction
# - Site structure analysis
# - Migration planning data
```

### 2. Create New Next.js Project
```bash
npx create-next-app@latest ai-art-store --typescript --tailwind --app
cd ai-art-store

# Install core dependencies
npm install @supabase/supabase-js stripe sharp zustand
npm install -D @types/sharp @playwright/test
```

### 3. Set Up Environment Variables
Create `.env.local`:
```env
# Database (use Supabase for quick setup)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Printify API
PRINTIFY_API_KEY=your_printify_key
PRINTIFY_SHOP_ID=your_shop_id

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# App
NEXT_PUBLIC_URL=http://localhost:3000
ADMIN_PASSWORD=your_secure_admin_password
```

## Priority Implementation Order

### Phase 1: Foundation (Start Here)
1. **Database Schema** - Create Supabase tables using the schema in Technical Specifications
2. **Basic Layout** - Header, footer, navigation matching current site style
3. **Product Display** - Homepage with product grid (static data first)
4. **Product Detail** - Individual product pages with images and descriptions

### Phase 2: Core E-commerce
1. **Shopping Cart** - Add to cart, view cart, update quantities
2. **Stripe Checkout** - Payment processing with webhook handling
3. **Order Management** - Save orders to database, send confirmations

### Phase 3: Printify Integration
1. **API Wrapper** - Create Printify API client
2. **Order Fulfillment** - Submit orders to Printify after payment
3. **Product Sync** - Create products in Printify from artwork

### Phase 4: Smart Features
1. **Image Analysis** - Implement Sharp.js image processing
2. **Admin Panel** - Upload and manage artwork
3. **Bulk Upload** - Process multiple artworks at once

## Key Files to Create First

### 1. Database Schema (`supabase/schema.sql`)
```sql
-- Copy from Technical Specifications document
-- Focus on: artworks, products, orders, order_items tables first
```

### 2. Product Types (`lib/types.ts`)
```typescript
export interface Artwork {
  id: string;
  title: string;
  description: string;
  prompt: string;
  file_url: string;
  thumbnail_url?: string;
  analysis?: ImageAnalysis;
  style: 'whimsy' | 'epic' | 'hybrid';
  tags: string[];
  active: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  artwork_id: string;
  artwork: Artwork;
  printify_product_id?: string;
  title: string;
  description: string;
  base_price: number;
  markup_percentage: number;
  active: boolean;
  printify_blueprint_id: number;
  print_provider_id: number;
  variants: ProductVariant[];
}

export interface ImageAnalysis {
  dimensions: { width: number; height: number; aspectRatio: number };
  hasAlpha: boolean;
  dominantColors: string[];
  complexity: 'low' | 'medium' | 'high';
  recommendedProducts: ProductRecommendation[];
}
```

### 3. Printify API Client (`lib/printify.ts`)
```typescript
class PrintifyAPI {
  private baseURL = 'https://api.printify.com/v1';
  private apiKey: string;
  private shopId: string;

  constructor() {
    this.apiKey = process.env.PRINTIFY_API_KEY!;
    this.shopId = process.env.PRINTIFY_SHOP_ID!;
  }

  async createProduct(artwork: Artwork, blueprintId: number): Promise<any> {
    // Implementation from Technical Specifications
  }

  async submitOrder(orderData: any): Promise<any> {
    // Implementation from Technical Specifications
  }
}
```

### 4. Homepage (`app/page.tsx`)
```typescript
import { ProductGrid } from '@/components/ProductGrid';
import { Hero } from '@/components/Hero';

export default async function HomePage() {
  // Fetch featured products from database
  const featuredProducts = await getFeaturedProducts();
  
  return (
    <main>
      <Hero />
      
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Featured Products</h2>
          <ProductGrid products={featuredProducts} />
        </div>
      </section>
      
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">Our Styles</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <StyleCard title="Whimsy" description="Lighthearted and beautiful" />
            <StyleCard title="Epic" description="Vast expanses and heroic adventure" />
            <StyleCard title="Hybrid" description="Two great tastes combined" />
          </div>
        </div>
      </section>
      
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Custom Requests</h2>
          <p className="text-lg mb-8">Wish we offered this art on that item? Just ask!</p>
          <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700">
            Submit Custom Request
          </button>
        </div>
      </section>
    </main>
  );
}
```

## Critical Success Factors

### 1. Start Simple
- Get basic product display working first
- Use static data initially, then connect to database
- Focus on core user flow: browse → add to cart → checkout

### 2. Match Current Site Style
- Use the screenshot analysis to replicate current design
- Preserve the "Whimsy/Epic/Hybrid" categorization
- Keep the custom request messaging

### 3. Optimize for AI Art
- Image-first design (large, high-quality product photos)
- Prominent prompt display on product pages
- Style-based navigation that makes sense for AI art

### 4. Build for Automation
- Design admin interfaces for bulk operations
- Make everything API-driven for future automation
- Plan for high-volume product creation

## Testing Strategy

### 1. Local Development Testing
```bash
# Test database connections
npm run db:test

# Test Printify API
npm run test:printify

# Test Stripe checkout
npm run test:stripe

# Run full test suite
npm test
```

### 2. Key User Flows to Test
- [ ] Browse products on homepage
- [ ] View product detail page
- [ ] Add product to cart
- [ ] Complete checkout with test card
- [ ] Receive order confirmation
- [ ] Admin can upload new artwork
- [ ] Admin can create products from artwork

## Deployment Checklist

### 1. Production Environment Setup
- [ ] Supabase production database
- [ ] Printify production API keys
- [ ] Stripe live keys (when ready)
- [ ] Custom domain configuration
- [ ] SSL certificate

### 2. Migration from Shopify
- [ ] Export all product data
- [ ] Download all product images
- [ ] Set up URL redirects
- [ ] Update DNS when ready
- [ ] Test order fulfillment end-to-end

## Support Resources

1. **Printify API Docs**: https://developers.printify.com/
2. **Stripe Integration Guide**: https://stripe.com/docs/checkout/quickstart
3. **Next.js App Router**: https://nextjs.org/docs/app
4. **Supabase Setup**: https://supabase.com/docs/guides/getting-started
5. **Tailwind CSS**: https://tailwindcss.com/docs

## Emergency Contacts & Rollback Plan

If issues arise:
1. **Rollback**: Keep Shopify active during transition
2. **DNS**: Can quickly revert DNS to Shopify
3. **Data**: All migration data backed up
4. **Orders**: Manual order processing capability as backup

---

**Start with Phase 1 and build incrementally. The goal is a working e-commerce site first, then add the smart AI art features that give you competitive advantages over standard Shopify stores.**