# AI Art Print-on-Demand Store - Custom Platform

## Project Overview

Build a custom e-commerce platform to replace the existing Shopify store at thevisiblewords.com, specifically optimized for AI-generated art and print-on-demand workflows via Printify API.

## Current State Analysis

### Site Analysis Tasks
1. **Playwright Screenshots**: Capture current site structure, product layouts, and user flows
2. **Content Audit**: Catalog existing products, descriptions, and categorization
3. **Design Elements**: Extract current branding, color schemes, and layout patterns
4. **Product Data**: Map current product types and their characteristics

### Migration Requirements
- Preserve existing product catalog and descriptions
- Maintain SEO-friendly URLs where possible
- Extract and optimize existing AI art prompts/metadata
- Preserve customer-facing copy that works

## Core Business Logic

### Intelligent Product Matching System
The platform should automatically determine optimal products for each AI artwork based on:

#### Image Analysis Criteria
1. **Aspect Ratio Detection**
   - Square (1:1): Stickers, coasters, wall art
   - Portrait (3:4, 4:5): Posters, book covers, phone cases
   - Landscape (4:3, 16:9): Mousepads, banners, wide prints
   - Tall portrait (2:3, 9:16): Bookmarks, phone wallpapers

2. **Resolution & Pixel Count**
   - High-res (>3000px): Large format prints, canvases, blankets
   - Medium-res (1500-3000px): Standard prints, apparel, notebooks
   - Lower-res (<1500px): Small items, stickers, digital products

3. **Alpha Channel/Transparency Detection**
   - **Has Alpha**: Apparel (t-shirts, hoodies), stickers, mugs
   - **No Alpha**: Journals, posters, blankets, full-coverage items

4. **Color Analysis**
   - Dark/light dominant colors affect product suitability
   - High contrast vs subtle gradients
   - Color palette extraction for automatic tagging

#### Product Suitability Matrix
```
Image Type → Recommended Products
─────────────────────────────────
Square + Alpha → T-shirts, Hoodies, Stickers
Square + No Alpha → Canvas prints, Ceramic tiles, Coasters
Portrait + High-res → Posters, Canvas prints, Phone cases
Landscape + Alpha → Mousepads, Laptop stickers
Complex/Detailed → High-res products only
Simple/Minimal → All product types
```

## Key Features

### Customer-Facing Features
- **Prompt Submission System**: Customers can submit text prompts for custom AI art
- **Smart Product Discovery**: Browse by style, color, theme, or intended product type
- **Preview Generator**: Show how artwork looks on different products
- **Style Categories**: Whimsical, Epic, Hybrid (as per current site)
- **Custom Request Workflow**: "Wish we offered this art on that item? Just ask!"

### Admin/Automation Features
- **Bulk Upload System**: Process multiple AI artworks simultaneously
- **Automated Product Creation**: Generate products across suitable categories
- **Printify Sync**: Real-time integration with Printify catalog and orders
- **Image Processing Pipeline**: Automatic upscaling, format conversion, analysis
- **Prompt Management**: Track and categorize successful prompts
- **Revenue Analytics**: Track performance by artwork, product type, etc.

## Technical Architecture

### Core Stack
- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL (via Supabase or similar)
- **Payment**: Stripe
- **Hosting**: Vercel or Railway
- **File Storage**: Cloudinary or AWS S3
- **Email**: Resend or SendGrid

### Key Integrations
- **Printify API**: Product catalog, order management, fulfillment
- **Image Analysis**: Sharp.js for processing, custom ML for classification
- **SEO**: Next.js built-in optimization
- **Analytics**: Plausible or Google Analytics

### Database Schema (High Level)
```sql
-- Artworks
artworks (id, title, description, prompt, file_url, metadata, created_at)

-- Products (Printify products created from artworks)
products (id, artwork_id, printify_product_id, title, price, active, created_at)

-- Orders
orders (id, stripe_payment_id, customer_email, total, status, created_at)

-- Order Items
order_items (id, order_id, product_id, quantity, price)

-- Customers (optional for marketing)
customers (id, email, name, created_at)
```

## Development Phases

### Phase 1: MVP Core (Week 1-2)
- Basic product catalog display
- Stripe payment integration
- Printify order creation
- Simple admin panel for product management

### Phase 2: Smart Features (Week 3-4)
- Image analysis and auto-categorization
- Bulk upload system
- Customer prompt submission
- Order management dashboard

### Phase 3: Advanced Automation (Week 5-6)
- AI art generation pipeline integration
- Advanced product matching algorithms
- Customer notification systems
- Analytics and reporting

### Phase 4: Growth Features (Week 7+)
- SEO optimization
- Marketing integrations
- Customer accounts
- Advanced customization options

## Success Metrics
- **Cost Reduction**: Sub-$50/month operating costs vs $200+ Shopify fees
- **Conversion Improvement**: Better UX for AI art discovery and purchasing
- **Automation Efficiency**: Reduce manual product creation time by 90%
- **Revenue Growth**: Enable scaling through better margins and automation

## Risk Mitigation
- **Payment Security**: Use Stripe's proven infrastructure
- **Uptime**: Deploy on reliable platforms with monitoring
- **Data Backup**: Automated backups for all content and orders
- **Gradual Migration**: Soft launch alongside Shopify before full switch

## Next Steps
1. Run Playwright analysis of current site
2. Set up development environment
3. Create initial database schema
4. Build core product display and checkout flow
5. Implement Printify integration
6. Add image analysis capabilities