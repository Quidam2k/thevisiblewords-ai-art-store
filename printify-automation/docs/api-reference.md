# Printify API Reference

## Overview

This document outlines the Printify API endpoints and data structures used by the automation tool.

## Authentication

All API requests require a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

All requests must also specify a User-Agent header. The value should be your application name or client type (e.g., "NodeJS", "Python", "Printify-Automation-Tool").

## Base URLs

- **V1 API**: `https://api.printify.com/v1/` (Primary API)
- **V2 API**: `https://api.printify.com/v2/` (New features, JSON:API compliant)

## Rate Limits

- **Global Limit**: 600 requests per minute
- **Product Publishing**: 200 requests per 30 minutes  
- **Error Rate**: Must not exceed 5% of total requests
- **Penalty**: 429 response code for exceeding limits

## Core Endpoints Used

### 1. Upload Images

**Endpoint**: `POST /uploads/images.json`

**Purpose**: Upload artwork to Printify's media library

**Request Body**:
```json
{
  "file_name": "image.png",
  "contents": "base64-encoded-content"
}
```

**Response**:
```json
{
  "id": "5d15ca551163cde90d7b2203",
  "file_name": "image.png",
  "height": 2000,
  "width": 2000,
  "size": 1138575,
  "mime_type": "image/png",
  "preview_url": "https://example.com/preview",
  "upload_time": "2020-01-09 07:29:43"
}
```

### 2. Create Product

**Endpoint**: `POST /shops/{shop_id}/products.json`

**Purpose**: Create a new product in the shop

**Request Body**:
```json
{
  "title": "AI Generated Art Print",
  "description": "Beautiful AI-generated artwork...",
  "safety_information": "Optional GPSR compliance information",
  "tags": ["ai-art", "digital", "modern"],
  "blueprint_id": 384,
  "print_provider_id": 1,
  "variants": [
    {
      "id": 45740,
      "price": 2000,
      "is_enabled": true
    }
  ],
  "print_areas": [
    {
      "variant_ids": [45740],
      "placeholders": [
        {
          "position": "front",
          "images": [
            {
              "id": "5d15ca551163cde90d7b2203",
              "x": 0.5,
              "y": 0.5,
              "scale": 1.0,
              "angle": 0
            }
          ]
        }
      ]
    }
  ]
}
```

**New Features**:
- `safety_information`: Optional field for GPSR compliance
- Enhanced variant properties including `is_printify_express_eligible`
- Support for text layers with font properties

### 3. Get Catalog Blueprints

**Endpoint**: `GET /catalog/blueprints.json`

**Purpose**: List available product types

**Response**:
```json
[
  {
    "id": 384,
    "title": "Unisex Heavy Cotton Tee",
    "brand": "Gildan",
    "model": "5000",
    "images": ["https://example.com/product.jpg"]
  }
]
```

### 4. Get Blueprint Variants

**Endpoint**: `GET /catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json`

**Purpose**: Get available sizes/colors for a product

**Query Parameters**:
- `show-out-of-stock`: Optional parameter
  - `0`: Show only in-stock variants (default)
  - `1`: Show all variants including out-of-stock

**Response**:
```json
{
  "variants": [
    {
      "id": 45740,
      "title": "White / S",
      "options": {
        "color": "White",
        "size": "S"
      },
      "placeholders": [
        {
          "position": "front",
          "height": 3995,
          "width": 3153
        }
      ],
      "is_available": true,
      "is_printify_express_eligible": true
    }
  ]
}
```

### 5. V2 API - Shipping Information

**Endpoint**: `GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/shipping.json`

**Purpose**: Get detailed shipping information (V2 API only)

**Available shipping methods**:
- `/shipping/standard.json`
- `/shipping/priority.json` 
- `/shipping/express.json`
- `/shipping/economy.json` (V2 only)

**Response**:
```json
{
  "data": [
    {
      "shippingType": "economy",
      "country": {"code": "US"},
      "variantId": 1,
      "handlingTime": {"from": 4, "to": 8},
      "shippingCost": {
        "firstItem": {"amount": 399, "currency": "USD"},
        "additionalItems": {"amount": 219, "currency": "USD"}
      }
    }
  ]
}
```

## Key Updates from Latest API

### Recent Changes (2025)
1. **V2 API Introduction**: New JSON:API compliant endpoints with enhanced features
2. **Economy Shipping**: New shipping option available only in V2 API
3. **GPSR Compliance**: New `safety_information` field for product compliance
4. **Enhanced Variant Properties**: Added eligibility flags for express shipping
5. **Product Pagination**: Reduced from 100 to 50 items per page (Oct 2024)
6. **Text Layer Support**: Enhanced support for text elements with font properties

### Shipping Method Updates
The shipping method codes have been updated:

| Code | Current Name | Transitional Name | Future Name |
|------|-------------|------------------|-------------|
| 1 | standard | standard | standard |
| 2 | express | priority | priority |
| 3 | - | printify_express | express |
| 4 | economy | economy | economy |

**Note**: `printify_express` will eventually be renamed to `express`, and current `express` will become `priority`.

### Product Template Structure

```python
{
    "blueprint_id": 384,          # Product type (t-shirt, mug, etc.)
    "print_provider_id": 1,       # Who prints the product
    "base_price": 2000,          # Price in cents
    "variants": [                # Available options
        {"id": 45740},           # Variant ID
        {"id": 45742}
    ],
    "print_areas": {             # Where to place design
        "front": {
            "position": "center",
            "scaling": "fit"
        }
    }
}
```

### Image Positioning

Printify uses a coordinate system from (0,0) to (1,1):
- `x: 0.5, y: 0.5` = center
- `scale: 1.0` = fill the print area
- `angle: 0` = no rotation

## Common Blueprint IDs

| Product Type | Blueprint ID |
|-------------|-------------|
| T-Shirt | 384 |
| Coffee Mug | 9 |
| Poster | 5 |
| Canvas | 6 |
| Phone Case | 12 |

## Error Handling

### Common Error Codes

- `400`: Bad Request (invalid data)
- `401`: Unauthorized (invalid token)
- `403`: Forbidden (insufficient permissions)
- `422`: Unprocessable Entity (validation errors)
- `429`: Too Many Requests (rate limited)

### Example Error Response

```json
{
  "error": "Validation failed",
  "message": "The given data was invalid",
  "errors": {
    "title": ["The title field is required"],
    "variants": ["At least one variant must be enabled"]
  }
}
```

## Image Requirements

### Technical Specifications
- **Formats**: PNG, JPG, JPEG
- **Resolution**: Minimum 300 DPI recommended
- **File Size**: Maximum 50MB via API
- **Color Mode**: RGB recommended

### Print Area Guidelines
- **T-Shirts**: 12" x 16" max print area
- **Mugs**: 8.5" x 3.5" wraparound
- **Posters**: Full bleed available
- **Canvas**: Multiple sizes available

## Integration Best Practices

### 1. Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=600):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

### 2. Error Retry Logic
```python
def retry_api_call(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt  # Exponential backoff
            time.sleep(delay)
```

### 3. Image Optimization
```python
def optimize_for_printify(image_path):
    with Image.open(image_path) as img:
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        max_size = (4000, 4000)
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Save with optimization
        output_path = "optimized_" + image_path
        img.save(output_path, "JPEG", quality=90, optimize=True)
        return output_path
```

## Testing with API

### Get Shop Information
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/shops.json
```

### Test Image Upload
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file_name":"test.png","url":"https://example.com/image.png"}' \
  https://api.printify.com/v1/uploads/images.json
```

### List Products
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/shops/SHOP_ID/products.json
```

## Webhook Integration (Future Enhancement)

Printify supports webhooks for real-time notifications:

### Available Events
- `product:publish:started`
- `order:created`
- `order:updated`
- `order:shipment:created`

### Webhook Setup
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"order:created","url":"https://yourapp.com/webhook"}' \
  https://api.printify.com/v1/shops/SHOP_ID/webhooks.json
```

This API reference provides the foundation for integrating with Printify's services for automated product creation.
