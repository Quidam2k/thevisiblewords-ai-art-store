# Setup Guide

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Printify account** with API access
3. **AI-generated images** with prompts stored in EXIF metadata

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `pyyaml` - Configuration file parsing
- `watchdog` - File system monitoring
- `pillow` - Image processing
- `pydantic` - Configuration validation
- `requests` - HTTP requests to Printify API

### 2. Printify API Setup

1. Log into your Printify account
2. Go to **My Profile → Connections**
3. Generate a **Personal Access Token**
4. Note your **Shop ID** (found in shop settings)

### 3. Configuration

1. Copy the example configuration:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` with your settings:

```yaml
printify:
  access_token: "YOUR_PRINTIFY_ACCESS_TOKEN"
  shop_id: YOUR_SHOP_ID

folders:
  - path: "./images/tshirts"
    template:
      blueprint_id: 384  # T-shirt blueprint
      print_provider_id: 1
      base_price: 2000  # Price in cents ($20.00)
      variants:
        - id: 45740  # Small
        - id: 45742  # Medium
        - id: 45744  # Large
      print_areas:
        front:
          position: "center"
          scaling: "fit"
    create_processed_folder: true
    create_failed_folder: true
```

### 4. Folder Structure Setup

The tool will automatically create the following structure:

```
images/
├── tshirts/           # Drop new images here
│   ├── processed/     # Successfully processed images
│   └── failed/        # Images that failed processing
└── mugs/              # Another product category
    ├── processed/
    └── failed/
```

## Configuration Options

### Printify Settings

- `access_token`: Your Printify API token
- `shop_id`: Your Printify shop ID
- `base_url`: API base URL (default: https://api.printify.com/v1)

### Folder Configuration

Each monitored folder requires:

- `path`: Local folder path to monitor
- `template`: Product template configuration
  - `blueprint_id`: Printify product type (t-shirt, mug, etc.)
  - `print_provider_id`: Which print provider to use
  - `base_price`: Base price in cents
  - `variants`: Available sizes/colors (get from Printify catalog API)
  - `print_areas`: Where to place the design

### Finding Blueprint and Variant IDs

Use the Printify API to find available options:

```bash
# Get all blueprints
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/catalog/blueprints.json

# Get variants for a blueprint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.printify.com/v1/catalog/blueprints/384/print_providers/1/variants.json
```

## Testing the Setup

1. **Validate configuration**:
   ```bash
   python config.py
   ```

2. **Test folder monitoring**:
   ```bash
   python main.py
   ```

3. **Add a test image** to one of your configured folders

4. **Check the logs** for processing status

## Image Requirements

Your AI-generated images should:
- Be in PNG, JPG, or JPEG format
- Contain the AI prompt in EXIF ImageDescription field
- Be at least 300 DPI for print quality
- Have dimensions suitable for the product type

## Common Issues

### "Configuration file not found"
- Ensure `config.yaml` exists in the project root
- Check file permissions

### "Invalid access token"
- Verify your Printify API token is correct
- Ensure the token has proper permissions

### "No prompt found in metadata"
- Check that your AI image generator saves prompts to EXIF data
- Use an EXIF viewer to verify metadata exists

### "Blueprint/variant not found"
- Verify blueprint_id and variant IDs using the Printify catalog API
- Ensure the print provider supports those variants

## Advanced Configuration

### Multiple Product Types

```yaml
folders:
  - path: "./images/tshirts"
    template:
      blueprint_id: 384
      # ... t-shirt config
  
  - path: "./images/mugs"
    template:
      blueprint_id: 9
      # ... mug config
```

### Custom Pricing

```yaml
template:
  base_price: 2000  # $20.00
  markup_percentage: 0.4  # 40% markup
```

### Processing Options

```yaml
processing:
  max_concurrent: 5
  retry_attempts: 3
  image_quality: 90
  auto_optimize: true
```

## Next Steps

Once configured, the system will:
1. Monitor your folders for new images
2. Extract AI prompts from metadata
3. Generate product titles and descriptions
4. Create Printify products automatically
5. Move processed images to appropriate folders

Check the logs in `logs/` directory for processing status and any errors.
