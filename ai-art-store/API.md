# API Reference - The Visible Words AI Art Store

## 📋 Overview

This document describes the REST API endpoints for the AI Art Store platform, including product management, Printify integration, and e-commerce functionality.

## 🔗 Base URL
```
Development: http://localhost:3000/api
Production: https://www.thevisiblewords.com/api
```

---

## 🛍️ Products API

### GET /api/products
Retrieve a paginated list of products with filtering and search capabilities.

#### Query Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number for pagination |
| `limit` | number | 12 | Number of products per page |
| `category` | string | - | Filter by product category |
| `style` | string | - | Filter by artwork style (WHIMSY, EPIC, HYBRID) |
| `search` | string | - | Search in titles, descriptions, and tags |
| `sortBy` | string | newest | Sort order (newest, price-low, price-high, popular) |
| `minPrice` | number | - | Minimum price filter (in cents) |
| `maxPrice` | number | - | Maximum price filter (in cents) |

#### Example Request
```bash
GET /api/products?category=Apparel&style=whimsy&search=dragon&page=1&limit=12
```

#### Response
```json
{
  "products": [
    {
      "id": "prod_123",
      "artworkId": "art_456",
      "printifyProductId": "printify_789",
      "title": "Whimsical Dragon T-Shirt",
      "description": "A magical dragon design perfect for fantasy lovers",
      "basePrice": 2499,
      "category": "Apparel",
      "images": ["https://example.com/image1.jpg"],
      "variants": [...],
      "featured": false,
      "active": true,
      "artwork": {
        "id": "art_456",
        "title": "Whimsical Dragon",
        "style": "WHIMSY",
        "tags": ["dragon", "fantasy", "magical"]
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 45,
    "totalPages": 4,
    "hasNext": true,
    "hasPrev": false
  },
  "filters": {
    "category": "Apparel",
    "style": "whimsy",
    "search": "dragon"
  }
}
```

### GET /api/products/[id]
Retrieve detailed information about a specific product.

#### Response
```json
{
  "product": {
    "id": "prod_123",
    "title": "Whimsical Dragon T-Shirt",
    "description": "A magical dragon design...",
    "basePrice": 2499,
    "variants": [
      {
        "id": 1,
        "price": 2499,
        "title": "S / White",
        "options": { "size": "S", "color": "White" },
        "available": true
      }
    ],
    "images": ["https://example.com/image1.jpg"],
    "artwork": {
      "id": "art_456",
      "title": "Whimsical Dragon",
      "description": "A magical dragon soaring...",
      "style": "WHIMSY",
      "tags": ["dragon", "fantasy", "magical"],
      "analysis": {
        "dominantColors": ["#4A90E2", "#50C878"],
        "recommendedProducts": [...]
      }
    },
    "printifyData": {
      // Live data from Printify API
    }
  },
  "relatedProducts": [
    // Array of related products
  ]
}
```

### POST /api/products
Create a new product (Admin only).

#### Request Body
```json
{
  "artworkId": "art_456",
  "title": "New Product",
  "description": "Product description",
  "basePrice": 2499,
  "category": "Apparel",
  "printifyBlueprintId": 3,
  "printProviderId": 1
}
```

---

## 🏷️ Categories API

### GET /api/categories
Retrieve dynamic category data, styles, price ranges, and popular tags.

#### Response
```json
{
  "categories": [
    {
      "name": "Apparel",
      "slug": "apparel",
      "count": 25
    },
    {
      "name": "Wall Art",
      "slug": "wall-art",
      "count": 18
    }
  ],
  "styles": [
    {
      "name": "WHIMSY",
      "slug": "whimsy",
      "count": 20
    },
    {
      "name": "EPIC",
      "slug": "epic",
      "count": 15
    }
  ],
  "priceRange": {
    "min": 1500,
    "max": 4999
  },
  "popularTags": [
    { "tag": "dragon", "count": 8 },
    { "tag": "fantasy", "count": 6 }
  ],
  "totalProducts": 43
}
```

---

## 🔄 Admin Printify Sync API

### POST /api/admin/printify/sync
Manage Printify product synchronization (Admin only).

#### Request Body - Sync All Products
```json
{
  "action": "sync-all"
}
```

#### Request Body - Sync Single Product
```json
{
  "action": "sync-single",
  "productId": "printify_product_123"
}
```

#### Response
```json
{
  "success": true,
  "message": "Sync completed: 25 products processed",
  "stats": {
    "total": 25,
    "synced": 25,
    "created": 3,
    "updated": 22,
    "errors": 0
  },
  "errors": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 💳 Checkout API

### POST /api/checkout
Create a Stripe checkout session for payment processing.

#### Request Body
```json
{
  "customerEmail": "customer@example.com",
  "customerName": "John Doe",
  "customerPhone": "+1234567890",
  "shippingAddress": {
    "firstName": "John",
    "lastName": "Doe",
    "address1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "country": "US",
    "zip": "12345"
  },
  "cartItems": [
    {
      "id": "cart_item_123",
      "productId": "prod_456",
      "title": "Dragon T-Shirt",
      "price": 2499,
      "quantity": 1,
      "variant": {
        "id": 1,
        "title": "M / Black",
        "options": { "size": "M", "color": "Black" }
      },
      "image": "https://example.com/image.jpg",
      "artworkStyle": "WHIMSY"
    }
  ]
}
```

#### Response
```json
{
  "sessionId": "cs_test_123456789",
  "url": "https://checkout.stripe.com/pay/cs_test_123456789"
}
```

---

## 📧 Newsletter API

### POST /api/newsletter
Subscribe to newsletter.

#### Request Body
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "source": "homepage"
}
```

#### Response
```json
{
  "message": "Successfully subscribed to newsletter"
}
```

---

## 🔐 Webhook APIs

### POST /api/webhooks/stripe
Handle Stripe webhook events for payment processing.

#### Supported Events
- `checkout.session.completed` - Payment successful, create order
- `payment_intent.succeeded` - Update order status to processing
- `payment_intent.payment_failed` - Mark order as failed

#### Headers Required
```
stripe-signature: whsec_signature_from_stripe
```

---

## 📊 Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE", // Optional error code
  "details": {} // Optional additional error details
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## 🔑 Authentication

Currently, the API uses basic environment-based authentication for admin endpoints. Future versions will implement:

- **JWT tokens** for user authentication
- **API keys** for external integrations
- **Role-based access control** for admin functions

### Admin Endpoints
The following endpoints require admin authentication:
- `POST /api/products`
- `PUT /api/products/[id]`
- `DELETE /api/products/[id]`
- `POST /api/admin/printify/sync`

---

## 📈 Rate Limiting

Current rate limits (to be implemented):
- **General API**: 100 requests per minute
- **Search API**: 50 requests per minute
- **Admin API**: 20 requests per minute

---

## 🧪 Testing

### Example API Calls

#### Test Product Search
```bash
curl "http://localhost:3000/api/products?search=dragon&style=epic"
```

#### Test Category Data
```bash
curl "http://localhost:3000/api/categories"
```

#### Test Product Details
```bash
curl "http://localhost:3000/api/products/prod_123"
```

### Development Database
Use the seeding command to populate test data:

```bash
npm run db:seed
```

This creates:
- 5 sample artworks with different styles
- 10+ products across multiple categories
- Realistic product variants and pricing
- Sample admin user

---

## 🔗 Integration Examples

### Frontend Integration
```typescript
// Fetch products with filtering
const response = await fetch('/api/products?category=Apparel&style=whimsy')
const { products, pagination } = await response.json()

// Get product details
const productResponse = await fetch(`/api/products/${productId}`)
const { product, relatedProducts } = await productResponse.json()
```

### Admin Integration
```typescript
// Sync products from Printify
const syncResponse = await fetch('/api/admin/printify/sync', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ action: 'sync-all' })
})
const syncResult = await syncResponse.json()
```

---

**Note**: This API is designed to work seamlessly with the Printify automation system and provides real-time integration with Stripe for payments and Printify for fulfillment.