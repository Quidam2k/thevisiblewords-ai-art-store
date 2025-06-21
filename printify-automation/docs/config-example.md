# Example Configuration File

```yaml
# Printify API Configuration
printify:
  access_token: "YOUR_PRINTIFY_ACCESS_TOKEN_HERE"
  shop_id: 123456
  base_url: "https://api.printify.com/v1"

# Monitored Folders Configuration
folders:
  # T-Shirt Products
  - path: "./images/tshirts"
    template:
      blueprint_id: 384           # Unisex Heavy Cotton Tee
      print_provider_id: 1        # Printful
      base_price: 2000           # $20.00 in cents
      variants:
        - id: 45740              # White / S
        - id: 45742              # White / M  
        - id: 45744              # White / L
        - id: 45746              # White / XL
        - id: 45748              # Black / S
        - id: 45750              # Black / M
        - id: 45752              # Black / L
        - id: 45754              # Black / XL
      print_areas:
        front:
          position: "center"
          scaling: "fit"
    create_processed_folder: true
    create_failed_folder: true

  # Coffee Mug Products  
  - path: "./images/mugs"
    template:
      blueprint_id: 9             # 11oz Coffee Mug
      print_provider_id: 5        # Print Provider
      base_price: 1500           # $15.00 in cents
      variants:
        - id: 17887              # White mug
        - id: 17888              # Black mug
      print_areas:
        front:
          position: "center"
          scaling: "fill"
    create_processed_folder: true
    create_failed_folder: true

  # Poster Products
  - path: "./images/posters"
    template:
      blueprint_id: 5             # Premium Poster
      print_provider_id: 3        # Print Provider
      base_price: 2500           # $25.00 in cents
      variants:
        - id: 29102              # 8x10
        - id: 29103              # 11x14  
        - id: 29104              # 16x20
        - id: 29105              # 18x24
      print_areas:
        front:
          position: "center"
          scaling: "fill"
    create_processed_folder: true
    create_failed_folder: true

  # Canvas Prints
  - path: "./images/canvas"
    template:
      blueprint_id: 6             # Canvas Print
      print_provider_id: 7        # Print Provider
      base_price: 3500           # $35.00 in cents
      variants:
        - id: 19483              # 8x10
        - id: 19484              # 12x16
        - id: 19485              # 16x20
        - id: 19486              # 20x24
      print_areas:
        front:
          position: "center"
          scaling: "fill"
    create_processed_folder: true
    create_failed_folder: true

# Processing Configuration (Optional)
processing:
  max_concurrent_uploads: 5      # Number of simultaneous uploads
  retry_attempts: 3              # Number of retry attempts for failed uploads
  retry_delay: 5                 # Delay between retries in seconds
  image_quality: 90              # JPEG quality for optimization (0-100)
  auto_optimize: true            # Automatically optimize images
  max_image_size_mb: 10          # Maximum image size in MB

# Metadata Processing Configuration (Optional)
metadata:
  title_max_length: 60           # Maximum title length
  max_tags: 10                   # Maximum number of tags per product
  style_keywords:                # Keywords to identify art styles
    - "realistic"
    - "anime"
    - "watercolor"
    - "oil painting"
    - "digital art"
    - "sketch"
    - "abstract"
  blacklist_words:               # Words to remove from prompts
    - "high quality"
    - "detailed"
    - "beautiful"
    - "8k"
    - "4k"
    - "ultra realistic"
    - "masterpiece"

# Logging Configuration (Optional)
logging:
  level: "INFO"                  # DEBUG, INFO, WARNING, ERROR
  file: "logs/automation.log"    # Log file path
  max_size_mb: 10               # Maximum log file size
  backup_count: 5               # Number of backup log files to keep
```

## Configuration Notes

### Finding Your Printify Credentials

1. **Access Token**: 
   - Go to Printify Dashboard → My Profile → Connections
   - Generate a Personal Access Token
   - Copy the token (it's only shown once!)

2. **Shop ID**:
   - Go to your Printify shop settings
   - The shop ID is in the URL or shop details

### Finding Blueprint and Variant IDs

Use the Printify API to discover available products:

```bash
# List all blueprints
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/catalog/blueprints.json

# Get variants for a specific blueprint and provider
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/catalog/blueprints/384/print_providers/1/variants.json
```

### Common Blueprint IDs

| Product | Blueprint ID | Description |
|---------|-------------|-------------|
| 384 | T-Shirt | Unisex Heavy Cotton Tee |
| 9 | Mug | 11oz Coffee Mug |
| 5 | Poster | Premium Poster |
| 6 | Canvas | Canvas Print |
| 12 | Phone Case | Various phone models |
| 77 | Hoodie | Unisex Heavy Blend Hoodie |

### Folder Structure

After configuration, your folder structure will look like:

```
images/
├── tshirts/
│   ├── new_ai_art.png         # Drop new images here
│   ├── processed/             # Successfully processed
│   └── failed/                # Failed processing
├── mugs/
│   ├── processed/
│   └── failed/
├── posters/
│   ├── processed/
│   └── failed/
└── canvas/
    ├── processed/
    └── failed/
```

### Pricing Strategy

Base prices are in cents:
- `2000` = $20.00
- `1500` = $15.00
- `2500` = $25.00

Consider your costs and desired profit margins when setting prices.

### Print Area Configuration

- **position**: "center", "top", "bottom", "left", "right"
- **scaling**: 
  - "fit" = scale to fit within print area
  - "fill" = scale to fill entire print area
  - "stretch" = stretch to exact dimensions

### Advanced Options

You can add multiple templates per folder for different product variations, or create separate folders for different art styles or categories.
