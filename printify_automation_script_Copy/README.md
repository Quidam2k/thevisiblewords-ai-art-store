# 🚀 Enhanced Printify Automation Tool

An intelligent, AI-powered system for processing AI-generated images and automatically creating Printify products with smart tag generation, image optimization, and advanced error handling.

## ✨ Key Features

### 🧠 AI-Powered Processing
- **Smart Tag Generation** - Automatically extracts relevant tags from AI prompts using advanced text analysis
- **Intelligent Title Generation** - Creates compelling product titles from AI prompts
- **Enhanced Description Creation** - Generates detailed product descriptions with context

### 🖼️ Advanced Image Processing
- **Automatic Optimization** - Resizes and optimizes images for best print quality
- **Multi-Format Support** - Handles PNG, JPG, JPEG with intelligent format conversion
- **EXIF Data Extraction** - Comprehensive metadata extraction including AI prompts
- **Image Validation** - Validates images meet Printify requirements before upload

### 🎯 Multi-Position Printing
- **Flexible Print Areas** - Supports front, back, sleeves, pockets, and specialty positions
- **Smart Position Recommendations** - AI suggests optimal print positions based on image characteristics
- **Automatic Scaling** - Intelligent image scaling for different print areas

### 💰 Configurable Pricing
- **Pricing Tiers** - Basic, Premium, Luxury, and Custom pricing strategies
- **Automatic Markup** - Configurable markup percentages with min/max constraints
- **Product-Specific Pricing** - Different pricing for different product types

### 🛡️ Enterprise-Grade Error Handling
- **Intelligent Retry Logic** - Exponential backoff for failed requests
- **Comprehensive Error Categorization** - Network, API, Image, Configuration error types
- **Recovery Suggestions** - Actionable suggestions for error resolution
- **Error Analytics** - Track error patterns and success rates

### 🌐 Modern Web Interface
- **Gradio-Based UI** - Clean, responsive web interface
- **Real-Time Progress** - Detailed progress tracking with substeps
- **Multi-Tab Organization** - Organized workflow with dedicated sections
- **Mobile-Friendly** - Works on tablets and phones

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd printify-automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `config.json` in the project directory:

```json
{
  "api": {
    "access_token": "your_printify_access_token",
    "shop_id": "your_shop_id"
  }
}
```

Get your credentials from [Printify Dashboard → API](https://printify.com/app/account/api)

### 3. Run the Application

```bash
python app.py
```

Open your browser to `http://localhost:7860`

### 4. Start Creating Products

1. **Configure Products** - Add product types using Printify catalog links
2. **Upload Images** - Drop AI-generated images with EXIF metadata
3. **Watch the Magic** - Automatic processing with smart tags and optimization

## 📁 Project Structure

```
printify-automation/
├── app.py                     # Main Gradio application
├── config.json               # User configuration
├── requirements.txt           # Python dependencies
├── src/                       # Enhanced modules
│   ├── tag_generator.py       # Smart tag generation
│   ├── config_manager.py      # Configuration management
│   ├── image_processor.py     # Image processing & optimization
│   ├── api_client.py          # Enhanced Printify API client
│   ├── error_handler.py       # Advanced error handling
│   ├── print_area_manager.py  # Multi-position print support
│   ├── gui.py                 # Legacy GUI (archived)
│   ├── upload.py              # Legacy upload logic
│   └── utils.py               # Utility functions
├── docs/                      # Documentation
│   ├── api-reference.md       # Printify API documentation
│   ├── architecture.md        # System architecture
│   ├── setup-guide.md         # Detailed setup guide
│   └── requirements.md        # Dependency information
├── archive/                   # Legacy files
└── development-notes.md       # Development history & notes
```

## ⚙️ Advanced Configuration

### Pricing Tiers

```json
{
  "pricing_tiers": {
    "basic": {
      "base_price": 1499,
      "markup_percentage": 0.0,
      "min_price": 999,
      "max_price": 9999
    },
    "premium": {
      "base_price": 1999,
      "markup_percentage": 15.0,
      "min_price": 1499,
      "max_price": 4999
    }
  }
}
```

### Product Settings

```json
{
  "product_settings": [
    {
      "blueprint_id": 384,
      "name": "Unisex Heavy Cotton Tee",
      "category": "apparel",
      "pricing_tier": "basic",
      "print_positions": ["front", "back"],
      "default_variants": [],
      "image_requirements": {
        "min_width": 2400,
        "min_height": 2400,
        "dpi": 300
      }
    }
  ]
}
```

### Image Processing

```json
{
  "image_processing": {
    "max_width": 4000,
    "max_height": 4000,
    "quality": 90,
    "format": "JPEG",
    "optimize": true,
    "auto_orient": true,
    "strip_metadata": false
  }
}
```

### Tag Generation

```json
{
  "tag_settings": {
    "max_tags": 15,
    "min_tag_length": 3,
    "include_style_tags": true,
    "include_color_tags": true,
    "include_mood_tags": true,
    "custom_tag_templates": ["ai-art", "digital-art"]
  }
}
```

## 🎯 Supported Product Types

| Product | Blueprint ID | Supported Positions | Print Requirements |
|---------|-------------|-------------------|-------------------|
| **T-Shirts** | 384 | Front, Back, Sleeves, Pocket | 2400x2400px min |
| **Hoodies** | Various | Front, Back, Sleeves | 2400x2400px min |
| **Posters** | 5 | Front | 3000x3000px min |
| **Canvas** | 6 | Front | 3600x3600px min |
| **Mugs** | 9 | Front, Wrap-around, Handle | 2000x1200px min |
| **Phone Cases** | 12 | Front, Back | 1800x3200px min |
| **Tote Bags** | Various | Front, Back | 2400x2400px min |
| **Notebooks** | Various | Front, Back, Inside | 2100x2700px min |

## 🛠️ API Features

### Latest Printify API Integration
- **V1 & V2 API Support** - Uses latest API endpoints and features
- **Enhanced Error Responses** - Detailed error messages with validation details
- **GPSR Compliance** - Automatic safety information fields
- **Rate Limiting** - Intelligent rate limiting with 600 RPM global, 200/30min products
- **Connection Pooling** - Efficient HTTP connection reuse

### Rate Limiting & Performance
- **Intelligent Throttling** - Respects Printify's rate limits automatically
- **Exponential Backoff** - Smart retry logic for failed requests
- **Batch Processing** - Efficient bulk operations
- **Connection Management** - Persistent HTTP sessions for better performance

## 📊 Analytics & Monitoring

### Error Tracking
- **Comprehensive Logging** - All operations logged with context
- **Error Categorization** - Network, API, Image, Configuration errors
- **Recovery Analytics** - Track success rates of error recovery
- **Pattern Detection** - Identify recurring issues automatically

### Performance Metrics
- **Upload Success Rates** - Track successful vs failed uploads
- **Processing Times** - Monitor image processing and API response times
- **Queue Depth** - Monitor processing pipeline efficiency
- **Resource Usage** - Track memory and CPU usage patterns

## 🧪 Testing & Automation

### Compatible with Modern Testing Tools
- **Puppeteer Integration** - Automate web interface testing
- **Playwright Support** - Cross-browser testing capabilities
- **API Testing** - Comprehensive API integration tests
- **Image Processing Tests** - Validate image optimization pipeline

### Example Puppeteer Test

```javascript
const puppeteer = require('puppeteer');

async function testUpload() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:7860');
  
  // Test image upload workflow
  const fileInput = await page.$('input[type="file"]');
  await fileInput.uploadFile('test-image.png');
  
  await page.click('button:contains("Smart Upload")');
  await page.waitForSelector('.success-message');
  
  await browser.close();
}
```

## 🔒 Security & Best Practices

### Security Features
- **External Configuration** - API credentials stored in external files
- **Input Validation** - All inputs validated and sanitized
- **Error Sanitization** - Sensitive data excluded from logs
- **Rate Limiting** - Built-in protection against API abuse

### Best Practices
- **Backup Configurations** - Automatic configuration backups
- **Graceful Degradation** - Continues operation during partial failures
- **Resource Cleanup** - Automatic cleanup of temporary files
- **Memory Management** - Efficient memory usage for large images

## 🚀 Deployment Options

### Local Development
```bash
python app.py
# Runs on http://localhost:7860
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 7860
CMD ["python", "app.py"]
```

### Cloud Deployment
- **Gradio Spaces** - Deploy to Hugging Face Spaces
- **AWS/GCP/Azure** - Deploy to any cloud provider
- **Heroku** - Simple cloud deployment
- **Railway** - Modern deployment platform

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest`
4. Start development server: `python app.py`

### Code Quality
- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing framework

## 📈 Roadmap

### Upcoming Features
- [ ] **Webhook Integration** - Real-time order notifications
- [ ] **Multi-Platform Support** - Redbubble, Society6, Etsy integration
- [ ] **Advanced Analytics** - Sales performance tracking
- [ ] **Batch Templates** - Save and reuse product configurations
- [ ] **AI Enhancement** - Further AI-powered optimizations

### Performance Improvements
- [ ] **Parallel Processing** - Concurrent image processing
- [ ] **Caching Layer** - Cache API responses and processed images
- [ ] **Database Integration** - Replace JSON files with proper database
- [ ] **Queue System** - Background job processing

## 🆘 Support

### Getting Help
- **Configuration Issues** - Check the Configuration tab in the web interface
- **API Problems** - Verify credentials and check error logs
- **Image Issues** - Use the Image Analysis tool in the Tools tab
- **Performance** - Review the Analytics tab for bottlenecks

### Common Issues
- **Rate Limiting** - Tool automatically handles Printify rate limits
- **Image Too Large** - Images are automatically optimized
- **Missing EXIF** - Tool generates fallback content
- **Network Errors** - Automatic retry with exponential backoff

### Error Recovery
The tool includes intelligent error recovery:
1. **Automatic Retry** - Failed operations retry automatically
2. **Graceful Degradation** - Continues processing other images
3. **Detailed Logging** - Comprehensive error information
4. **Recovery Suggestions** - Actionable steps to resolve issues

## 📄 License

MIT License - see LICENSE file for details.

---

**Enhanced with ❤️ for the AI art community**

*This tool represents a significant evolution from the original Printify automation script, incorporating modern web technologies, intelligent processing, and enterprise-grade reliability.*