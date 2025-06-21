# Technical Specifications - AI Art Store

## Architecture Overview

### Frontend Application (Next.js 14)
```
/app
├── (store)/
│   ├── page.tsx                 # Homepage with featured products
│   ├── products/
│   │   ├── page.tsx            # Product listing with filters
│   │   ├── [id]/page.tsx       # Individual product page
│   │   └── category/[slug]/page.tsx # Category pages
│   ├── cart/page.tsx           # Shopping cart
│   ├── checkout/page.tsx       # Checkout flow
│   └── success/page.tsx        # Order confirmation
├── admin/
│   ├── dashboard/page.tsx      # Admin dashboard
│   ├── products/page.tsx       # Product management
│   ├── orders/page.tsx         # Order management
│   ├── artworks/page.tsx       # Artwork upload/management
│   └── analytics/page.tsx      # Sales analytics
├── api/
│   ├── products/route.ts       # Product CRUD operations
│   ├── orders/route.ts         # Order management
│   ├── printify/route.ts       # Printify webhook handlers
│   ├── stripe/route.ts         # Stripe webhook handlers
│   ├── images/route.ts         # Image processing endpoints
│   └── analysis/route.ts       # Image analysis API
└── components/
    ├── ui/                     # Reusable UI components
    ├── product/                # Product-related components
    ├── admin/                  # Admin panel components
    └── forms/                  # Form components
```

## Image Analysis System

### Image Processing Pipeline
```typescript
interface ImageAnalysis {
  dimensions: {
    width: number;
    height: number;
    aspectRatio: number;
  };
  hasAlpha: boolean;
  dominantColors: string[];
  complexity: 'low' | 'medium' | 'high';
  recommendedProducts: ProductRecommendation[];
}

interface ProductRecommendation {
  printifyBlueprintId: number;
  confidence: number;
  reason: string;
  variants: number[];
}
```

### Product Matching Algorithm
```typescript
function analyzeImageForProducts(analysis: ImageAnalysis): ProductRecommendation[] {
  const recommendations: ProductRecommendation[] = [];
  
  // Alpha channel logic
  if (analysis.hasAlpha) {
    // Transparent images work well on apparel and standalone items
    recommendations.push({
      printifyBlueprintId: 5,  // T-shirt
      confidence: 0.9,
      reason: "Transparent background ideal for apparel",
      variants: getVariantsForSize(analysis.dimensions)
    });
  } else {
    // Non-transparent images work for full-coverage items
    recommendations.push({
      printifyBlueprintId: 384, // Canvas
      confidence: 0.8,
      reason: "Full image coverage suitable for canvas prints",
      variants: []
    });
  }
  
  // Aspect ratio logic
  const ratio = analysis.dimensions.aspectRatio;
  if (Math.abs(ratio - 1) < 0.1) { // Square-ish
    recommendations.push({
      printifyBlueprintId: 1062, // Stickers
      confidence: 0.85,
      reason: "Square format perfect for stickers",
      variants: []
    });
  }
  
  // Resolution logic
  const pixelCount = analysis.dimensions.width * analysis.dimensions.height;
  if (pixelCount > 9000000) { // >3000x3000
    recommendations.push({
      printifyBlueprintId: 7,   // Canvas large
      confidence: 0.9,
      reason: "High resolution supports large format printing",
      variants: []
    });
  }
  
  return recommendations.sort((a, b) => b.confidence - a.confidence);
}
```

## Database Schema

### Core Tables
```sql
-- Artworks table
CREATE TABLE artworks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  prompt TEXT,
  file_url TEXT NOT NULL,
  thumbnail_url TEXT,
  analysis JSONB, -- Store ImageAnalysis result
  tags TEXT[],
  style VARCHAR(50), -- 'whimsical', 'epic', 'hybrid'
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Products table (generated from artworks)
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  artwork_id UUID REFERENCES artworks(id),
  printify_product_id VARCHAR(100) UNIQUE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  base_price INTEGER NOT NULL, -- in cents
  markup_percentage INTEGER DEFAULT 100, -- 100% markup = 2x cost
  active BOOLEAN DEFAULT true,
  printify_blueprint_id INTEGER NOT NULL,
  print_provider_id INTEGER NOT NULL,
  variants JSONB, -- Store variant pricing and options
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Orders table
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_payment_intent_id VARCHAR(100) UNIQUE,
  customer_email VARCHAR(255) NOT NULL,
  customer_name VARCHAR(255),
  shipping_address JSONB NOT NULL,
  total_amount INTEGER NOT NULL, -- in cents
  status VARCHAR(50) DEFAULT 'pending', -- pending, paid, shipped, delivered, cancelled
  printify_order_id VARCHAR(100),
  tracking_info JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Order items table
CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  printify_variant_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price INTEGER NOT NULL, -- in cents
  total_price INTEGER NOT NULL, -- in cents
  created_at TIMESTAMP DEFAULT now()
);

-- Custom requests table
CREATE TABLE custom_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_email VARCHAR(255) NOT NULL,
  customer_name VARCHAR(255),
  prompt TEXT NOT NULL,
  preferred_products TEXT[], -- array of product types they want
  status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, declined
  admin_notes TEXT,
  estimated_completion DATE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_artworks_style ON artworks(style);
CREATE INDEX idx_artworks_active ON artworks(active) WHERE active = true;
CREATE INDEX idx_products_artwork ON products(artwork_id);
CREATE INDEX idx_products_printify ON products(printify_product_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

## API Integrations

### Printify API Wrapper
```typescript
class PrintifyAPI {
  private baseURL = 'https://api.printify.com/v1';
  private apiKey: string;
  
  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }
  
  async createProduct(artwork: Artwork, blueprintId: number): Promise<PrintifyProduct> {
    // Upload artwork to Printify
    const uploadedImage = await this.uploadImage(artwork.file_url, artwork.title);
    
    // Create product with uploaded image
    const productData = {
      title: artwork.title,
      description: artwork.description,
      blueprint_id: blueprintId,
      print_provider_id: this.getBestPrintProvider(blueprintId),
      variants: this.generateVariants(blueprintId),
      print_areas: [{
        variant_ids: this.getAllVariantIds(blueprintId),
        placeholders: [{
          position: 'front',
          images: [{
            id: uploadedImage.id,
            x: 0.5,
            y: 0.5,
            scale: 1,
            angle: 0
          }]
        }]
      }]
    };
    
    return this.request('POST', `/shops/${this.shopId}/products.json`, productData);
  }
  
  async submitOrder(orderData: OrderSubmission): Promise<PrintifyOrder> {
    return this.request('POST', `/shops/${this.shopId}/orders.json`, orderData);
  }
  
  private async request(method: string, endpoint: string, data?: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: data ? JSON.stringify(data) : undefined
    });
    
    if (!response.ok) {
      throw new Error(`Printify API error: ${response.statusText}`);
    }
    
    return response.json();
  }
}
```

### Stripe Integration
```typescript
// Checkout session creation
export async function POST(request: Request) {
  const { cartItems, customerInfo } = await request.json();
  
  const lineItems = cartItems.map((item: CartItem) => ({
    price_data: {
      currency: 'usd',
      product_data: {
        name: item.title,
        images: [item.image_url]
      },
      unit_amount: item.price // in cents
    },
    quantity: item.quantity
  }));
  
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: lineItems,
    mode: 'payment',
    success_url: `${process.env.NEXT_PUBLIC_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/cart`,
    customer_email: customerInfo.email,
    metadata: {
      order_data: JSON.stringify({ cartItems, customerInfo })
    }
  });
  
  return NextResponse.json({ sessionId: session.id });
}
```

## Bulk Upload System

### Artwork Processing Flow
```typescript
interface BulkUploadJob {
  id: string;
  artworks: File[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results: ArtworkUploadResult[];
}

async function processBulkUpload(files: File[]): Promise<BulkUploadJob> {
  const job: BulkUploadJob = {
    id: generateId(),
    artworks: files,
    status: 'pending',
    progress: 0,
    results: []
  };
  
  // Process each artwork
  for (let i = 0; i < files.length; i++) {
    try {
      const file = files[i];
      
      // 1. Upload to cloud storage
      const uploadedUrl = await uploadToCloudinary(file);
      
      // 2. Analyze image
      const analysis = await analyzeImage(uploadedUrl);
      
      // 3. Create artwork record
      const artwork = await createArtwork({
        title: extractTitleFromFilename(file.name),
        file_url: uploadedUrl,
        analysis
      });
      
      // 4. Generate products for recommended blueprints
      const products = await generateProductsForArtwork(artwork, analysis.recommendedProducts);
      
      job.results.push({
        artwork,
        products,
        status: 'success'
      });
      
    } catch (error) {
      job.results.push({
        filename: files[i].name,
        error: error.message,
        status: 'failed'
      });
    }
    
    job.progress = ((i + 1) / files.length) * 100;
  }
  
  job.status = 'completed';
  return job;
}
```

## Deployment Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...
DIRECT_URL=postgresql://... # for migrations

# External APIs
PRINTIFY_API_KEY=your_printify_key
PRINTIFY_SHOP_ID=your_shop_id
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# File Storage
CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

# App Config
NEXT_PUBLIC_URL=https://thevisiblewords.com
ADMIN_EMAIL=your_admin_email
```

### Vercel Deployment
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "functions": {
    "app/api/images/analyze/route.ts": {
      "maxDuration": 30
    },
    "app/api/bulk-upload/route.ts": {
      "maxDuration": 300
    }
  }
}
```

## Performance Considerations

### Image Optimization
- Use Next.js Image component for automatic optimization
- Generate multiple sizes for different screen densities
- Implement lazy loading for product grids
- Use WebP format where supported

### Caching Strategy
- Cache product data in Redis for faster page loads
- Use Next.js ISR for product pages
- Cache Printify API responses where appropriate
- Implement CDN caching for static assets

### Database Optimization
- Index frequently queried columns
- Use connection pooling
- Implement read replicas for heavy analytics queries
- Consider materialized views for complex reporting