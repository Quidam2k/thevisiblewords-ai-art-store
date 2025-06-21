# 🧪 Testing Guide - Enhanced Printify Automation Tool

This document provides comprehensive testing procedures for validating the Enhanced Printify Automation Tool functionality, both for manual testing and automated testing using MCP tools.

## 📋 Testing Overview

### Testing Objectives
1. **Functional Validation** - Verify all features work as expected
2. **Error Handling** - Confirm robust error recovery and user feedback
3. **Performance Testing** - Validate system performance under load
4. **Integration Testing** - Verify Printify API integration works correctly
5. **User Experience** - Ensure intuitive and responsive interface
6. **Configuration Testing** - Validate configuration management and validation

### Testing Environments
- **Local Development** - `http://localhost:7860`
- **Docker Container** - Containerized deployment testing
- **Production Environment** - Final deployment validation

## 🚀 Pre-Test Setup

### 1. Environment Preparation

```bash
# Clone and setup project
git clone <repository-url>
cd printify-automation

# Install dependencies
pip install -r requirements.txt

# Note: pytest is optional - tests can run without it
# Install optional testing dependencies if available:
pip install pytest playwright puppeteer selenium beautifulsoup4 || echo "Some testing dependencies unavailable"

# Setup test configuration
cp config.json config.test.json
```

### 2. Test Data Preparation

Create test images with EXIF metadata:
```python
# create_test_images.py
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import os

def create_test_image_with_prompt(filename, prompt, width=2000, height=2000):
    """Create test image with AI prompt in EXIF data"""
    # Create test image
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    
    # Add EXIF data with prompt
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    exif_dict["0th"][TAGS['ImageDescription']] = prompt
    
    # Save with EXIF
    img.save(filename, exif=exif_dict)
    print(f"Created test image: {filename} with prompt: {prompt}")

# Create test images
test_images = [
    ("test_landscape.jpg", "A serene mountain landscape at sunset with golden light", 3000, 2000),
    ("test_portrait.jpg", "Portrait of a woman with flowing hair in watercolor style", 2000, 3000),
    ("test_square.jpg", "Abstract geometric pattern in vibrant rainbow colors", 2400, 2400),
    ("test_wide.jpg", "Cyberpunk cityscape with neon lights and flying cars", 4000, 2000),
    ("test_large.jpg", "Fantasy dragon breathing fire in mystical forest", 5000, 5000)
]

for filename, prompt, w, h in test_images:
    create_test_image_with_prompt(f"test_data/{filename}", prompt, w, h)
```

### 3. Configuration Setup

```json
// config.test.json
{
  "api": {
    "access_token": "test_token_here",
    "shop_id": "test_shop_id",
    "base_url": "https://api.printify.com/v1",
    "user_agent": "Printify-Automation-Tool-Test"
  },
  "image_processing": {
    "max_width": 4000,
    "max_height": 4000,
    "quality": 90,
    "format": "JPEG"
  },
  "tag_settings": {
    "max_tags": 15,
    "min_tag_length": 3
  }
}
```

## 🔧 Manual Testing Procedures

### Test Suite 1: Basic Functionality

#### 1.1 Application Startup
**Objective**: Verify application starts correctly

**Steps**:
1. Run `python app.py`
2. Navigate to `http://localhost:7860`
3. Verify interface loads without errors
4. Check all tabs are accessible

**Expected Results**:
- ✅ Application starts without errors
- ✅ Web interface loads completely
- ✅ All tabs (Product Management, Enhanced Upload, Configuration, Analytics, Tools) are accessible
- ✅ No JavaScript errors in browser console

**Test Data**: N/A

---

#### 1.2 Configuration Status Check
**Objective**: Verify configuration validation works

**Steps**:
1. Go to Configuration tab
2. Check configuration status display
3. Click "Refresh Status" button
4. Verify error summary displays

**Expected Results**:
- ✅ Configuration status shows current state
- ✅ Missing credentials are clearly indicated
- ✅ Refresh button updates status
- ✅ Error summary shows recent errors (if any)

**Test Data**: Valid and invalid config.json files

---

#### 1.3 Image Analysis Tool
**Objective**: Verify image analysis functionality

**Steps**:
1. Go to Tools tab
2. Upload test image in "Image Preview & Analysis" section
3. Click "Analyze Image" button
4. Review analysis results

**Expected Results**:
- ✅ Image uploads successfully
- ✅ Analysis shows image dimensions
- ✅ EXIF prompt is extracted correctly
- ✅ Smart tags are generated
- ✅ Print position recommendations are provided
- ✅ Generated title appears reasonable

**Test Data**: `test_landscape.jpg` with known EXIF prompt

---

### Test Suite 2: Product Management

#### 2.1 Add Product via Catalog Link
**Objective**: Verify product addition from Printify catalog

**Steps**:
1. Go to Product Management tab
2. Enter valid Printify product link in text field
3. Click "Add Product" button
4. Verify product appears in product list

**Expected Results**:
- ✅ Product link is processed correctly
- ✅ Product appears in configured products list
- ✅ Success message is displayed
- ✅ Product list updates automatically

**Test Data**: 
```
# Valid Printify product links
https://printify.com/app/products/384/providers/1
https://printify.com/app/products/5/providers/28
```

---

#### 2.2 Product Management Operations
**Objective**: Verify product deletion and management

**Steps**:
1. Add multiple products using catalog links
2. Delete specific product by index
3. Clear all products
4. Verify operations update the product list

**Expected Results**:
- ✅ Product deletion works correctly
- ✅ Clear all removes all products
- ✅ Product list updates reflect changes
- ✅ Error handling for invalid indices

**Test Data**: Multiple valid product links

---

### Test Suite 3: Enhanced Upload Pipeline

#### 3.1 Single Image Upload
**Objective**: Verify complete upload pipeline for single image

**Steps**:
1. Configure at least one product in Product Management
2. Go to Enhanced Upload tab
3. Upload single test image
4. Click "Smart Upload & Create Products"
5. Monitor progress and results

**Expected Results**:
- ✅ Image uploads successfully
- ✅ Progress bar shows detailed steps
- ✅ Image is validated and optimized
- ✅ Smart tags are generated
- ✅ Product is created in Printify
- ✅ Success message with details
- ✅ Detailed results show all operations

**Test Data**: `test_square.jpg` (2400x2400px with good EXIF data)

---

#### 3.2 Batch Image Upload
**Objective**: Verify batch processing functionality

**Steps**:
1. Configure multiple products
2. Upload multiple test images (3-5 images)
3. Start batch upload process
4. Monitor progress for each image
5. Review detailed results

**Expected Results**:
- ✅ All images processed sequentially
- ✅ Progress shows current image and step
- ✅ Individual results for each image
- ✅ Failed images don't stop batch processing
- ✅ Final summary shows success/failure counts
- ✅ Error handling for problematic images

**Test Data**: Mix of valid and problematic test images

---

#### 3.3 Image Validation and Error Handling
**Objective**: Verify robust error handling for various image issues

**Steps**:
1. Upload oversized image (>50MB or >5000px)
2. Upload corrupted image file
3. Upload unsupported format
4. Upload image without EXIF data
5. Verify appropriate error messages

**Expected Results**:
- ✅ Oversized images are automatically optimized
- ✅ Corrupted images show clear error messages
- ✅ Unsupported formats are handled gracefully
- ✅ Missing EXIF data uses fallback content
- ✅ Processing continues for valid images

**Test Data**: Intentionally problematic image files

---

### Test Suite 4: Configuration Management

#### 4.1 Configuration Validation
**Objective**: Verify configuration validation system

**Steps**:
1. Go to Tools tab
2. Click "Validate Configuration"
3. Test with various configuration states:
   - Missing config.json
   - Invalid JSON syntax
   - Missing required fields
   - Invalid API credentials
   - Valid complete configuration

**Expected Results**:
- ✅ Missing configuration detected
- ✅ JSON syntax errors reported
- ✅ Missing fields identified
- ✅ Invalid credentials validation
- ✅ Valid configuration confirmed
- ✅ Clear, actionable error messages

**Test Data**: Various config.json files (valid, invalid, missing)

---

#### 4.2 Configuration Template Export
**Objective**: Verify configuration template generation

**Steps**:
1. Go to Tools tab
2. Click "Export Config Template"
3. Verify template file creation
4. Review template file contents

**Expected Results**:
- ✅ Template file created successfully
- ✅ Template includes all configuration sections
- ✅ Template has helpful comments and instructions
- ✅ Template follows correct JSON structure

**Test Data**: N/A

---

### Test Suite 5: Error Handling and Recovery

#### 5.1 Network Error Simulation
**Objective**: Verify network error handling

**Steps**:
1. Disconnect from internet or use invalid API endpoint
2. Attempt image upload
3. Verify error handling and recovery suggestions
4. Reconnect and retry operation

**Expected Results**:
- ✅ Network errors detected correctly
- ✅ User-friendly error messages displayed
- ✅ Recovery suggestions provided
- ✅ Retry functionality works when connection restored
- ✅ Error logged with appropriate context

**Test Data**: Valid images with network disconnection

---

#### 5.2 API Error Handling
**Objective**: Verify API error response handling

**Steps**:
1. Use invalid API credentials
2. Attempt operations requiring API access
3. Test rate limiting scenarios (if possible)
4. Verify error categorization and suggestions

**Expected Results**:
- ✅ Invalid credentials detected and reported
- ✅ API errors categorized correctly
- ✅ Rate limiting handled gracefully
- ✅ Actionable recovery suggestions provided
- ✅ Error context preserved for debugging

**Test Data**: Invalid API credentials, high-frequency requests

---

## 🧪 Unit Testing (No Dependencies Required)

### Running Individual Test Modules

The test suite can run without pytest or other external dependencies:

```bash
# Run individual test modules directly
python3 tests/test_config_manager.py
python3 tests/test_tag_generator.py  
python3 tests/test_pricing_monitor.py

# Run comprehensive test suite
python3 tests/run_tests.py

# Run MCP-compatible test runner (JSON output)
python3 tests/mcp_test_runner.py --suite all --json

# Run specific test suites
python3 tests/mcp_test_runner.py --suite core    # ConfigManager + TagGenerator  
python3 tests/mcp_test_runner.py --suite pricing # PricingMonitor + CostAnalyzer + PriceAdjuster

# Run API integration tests
python3 tests/test_api_client_basic.py
```

### Browser Testing with MCP Playwright Server

When MCP Playwright server is available, use these commands for comprehensive browser testing:

```bash
# Start the application first
python3 app.py

# Then use MCP Playwright server commands:
# 1. Navigate to application
mcp__playwright__browser_navigate("http://localhost:7860")

# 2. Take screenshot for visual verification  
mcp__playwright__browser_take_screenshot("app-loaded.png")

# 3. Test tab navigation
mcp__playwright__browser_click("Enhanced Upload tab", "tab_ref")

# 4. Test form interaction
mcp__playwright__browser_type("Product link field", "input_ref", "https://printify.com/catalog/...")
mcp__playwright__browser_click("Add Product button", "button_ref")

# 5. Test file upload
mcp__playwright__browser_file_upload(["/path/to/test/image.png"])
```

## 🤖 Automated Testing with MCP Tools

### Automated Test Suite Setup

#### 1. Playwright Integration Test

```python
# test_automated_workflow.py
import pytest
from playwright.sync_api import sync_playwright
import os
import json
import time

class TestPrintifyAutomation:
    def setup_class(self):
        """Setup test environment"""
        self.base_url = "http://localhost:7860"
        self.test_images_dir = "test_data"
        
    def test_application_startup(self):
        """Test application starts and loads correctly"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Navigate to application
            page.goto(self.base_url)
            
            # Verify page loads
            assert page.title() == "Enhanced Printify Automation Tool"
            
            # Verify all tabs are present
            tabs = ["Product Management", "Enhanced Upload", "Configuration", "Analytics", "Tools"]
            for tab in tabs:
                assert page.locator(f"text={tab}").is_visible()
            
            browser.close()
    
    def test_image_analysis_workflow(self):
        """Test complete image analysis workflow"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)
            
            # Navigate to Tools tab
            page.click("text=Tools")
            
            # Upload test image
            test_image = os.path.join(self.test_images_dir, "test_landscape.jpg")
            page.set_input_files("input[type='file']", test_image)
            
            # Click analyze
            page.click("text=🔍 Analyze Image")
            
            # Wait for results and verify
            page.wait_for_selector("text=Image Analysis", timeout=10000)
            analysis_text = page.locator("[label='Analysis Results']").input_value()
            
            assert "Image Analysis" in analysis_text
            assert "Generated Tags" in analysis_text
            assert "Print Position Recommendations" in analysis_text
            
            browser.close()
    
    def test_product_management_workflow(self):
        """Test product addition and management"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)
            
            # Navigate to Product Management
            page.click("text=Product Management")
            
            # Add test product
            test_product_link = "https://printify.com/app/products/384/providers/1"
            page.fill("input[placeholder*='Printify catalog link']", test_product_link)
            page.click("text=Add Product")
            
            # Verify product appears in list
            page.wait_for_selector("text=Blueprint ID: 384", timeout=5000)
            product_list = page.locator("[label='Configured Products']").input_value()
            assert "384" in product_list
            
            browser.close()
    
    def test_upload_workflow_simulation(self):
        """Test upload workflow without actual API calls"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)
            
            # Setup: Add a product first
            page.click("text=Product Management")
            page.fill("input[placeholder*='Printify catalog link']", "https://printify.com/app/products/384/providers/1")
            page.click("text=Add Product")
            page.wait_for_timeout(2000)
            
            # Navigate to Enhanced Upload
            page.click("text=Enhanced Upload")
            
            # Upload test images
            test_images = [
                os.path.join(self.test_images_dir, "test_square.jpg"),
                os.path.join(self.test_images_dir, "test_landscape.jpg")
            ]
            page.set_input_files("input[type='file'][multiple]", test_images)
            
            # Note: Without valid API credentials, this will fail
            # But we can test the UI workflow up to API call
            page.click("text=🚀 Smart Upload & Create Products")
            
            # Verify error handling for missing credentials
            page.wait_for_selector("text=Please configure", timeout=10000)
            status_text = page.locator("[label='Status']").input_value()
            assert "configure" in status_text.lower()
            
            browser.close()
    
    def test_configuration_validation(self):
        """Test configuration validation workflow"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.base_url)
            
            # Navigate to Tools tab
            page.click("text=Tools")
            
            # Test configuration validation
            page.click("text=✅ Validate Configuration")
            
            # Verify validation results
            page.wait_for_timeout(2000)
            validation_result = page.locator("[label='Tool Results']").input_value()
            assert len(validation_result) > 0
            
            # Test config template export
            page.click("text=📥 Export Config Template")
            page.wait_for_timeout(1000)
            export_result = page.locator("[label='Tool Results']").input_value()
            assert "template" in export_result.lower()
            
            browser.close()

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

#### 2. Performance Testing Script

```python
# test_performance.py
import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
import requests

class PerformanceTest:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url
        
    def test_application_response_time(self):
        """Test application response times"""
        start_time = time.time()
        response = requests.get(self.base_url)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0, f"Response time {response_time}s exceeds 3s threshold"
        
        print(f"✅ Application response time: {response_time:.2f}s")
        
    def test_concurrent_requests(self, num_requests=10):
        """Test handling of concurrent requests"""
        def make_request():
            response = requests.get(self.base_url)
            return response.status_code == 200
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        success_rate = sum(results) / len(results) * 100
        
        assert success_rate >= 95, f"Success rate {success_rate}% below 95% threshold"
        print(f"✅ Concurrent requests: {success_rate}% success rate in {total_time:.2f}s")
        
    def test_memory_usage_simulation(self):
        """Simulate memory usage with large image processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate large image processing
        from PIL import Image
        large_images = []
        for i in range(5):
            img = Image.new('RGB', (4000, 4000), color=(i*50, i*40, i*30))
            large_images.append(img)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Cleanup
        del large_images
        
        print(f"✅ Memory usage test: {memory_increase:.1f}MB increase for large images")
        assert memory_increase < 500, f"Memory increase {memory_increase}MB exceeds 500MB threshold"

# Run performance tests
if __name__ == "__main__":
    perf_test = PerformanceTest()
    perf_test.test_application_response_time()
    perf_test.test_concurrent_requests()
    perf_test.test_memory_usage_simulation()
```

#### 3. API Integration Testing

```python
# test_api_integration.py
import pytest
import json
import os
from unittest.mock import Mock, patch
import sys
sys.path.append('src')

from api_client import PrintifyAPIClient
from config_manager import ConfigManager
from image_processor import ImageProcessor

class TestAPIIntegration:
    def setup_class(self):
        """Setup test environment with mock data"""
        self.mock_config = {
            "access_token": "test_token",
            "shop_id": "12345",
            "user_agent": "Test-Agent"
        }
        
    @patch('requests.Session.request')
    def test_api_client_initialization(self, mock_request):
        """Test API client initializes correctly"""
        client = PrintifyAPIClient(
            self.mock_config["access_token"],
            self.mock_config["shop_id"],
            self.mock_config
        )
        
        assert client.access_token == "test_token"
        assert client.shop_id == "12345"
        assert client.user_agent == "Test-Agent"
        
    @patch('requests.Session.request')
    def test_image_upload_simulation(self, mock_request):
        """Test image upload with mocked API response"""
        # Mock successful upload response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "test_image_id_123",
            "preview_url": "https://example.com/preview.jpg"
        }
        mock_request.return_value = mock_response
        
        client = PrintifyAPIClient(
            self.mock_config["access_token"],
            self.mock_config["shop_id"],
            self.mock_config
        )
        
        result = client.upload_image("test.jpg", "base64_content_here")
        
        assert result.success == True
        assert result.data["id"] == "test_image_id_123"
        
    @patch('requests.Session.request')
    def test_product_creation_simulation(self, mock_request):
        """Test product creation with mocked API response"""
        # Mock successful product creation
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "product_123",
            "title": "Test Product"
        }
        mock_request.return_value = mock_response
        
        client = PrintifyAPIClient(
            self.mock_config["access_token"],
            self.mock_config["shop_id"],
            self.mock_config
        )
        
        product_data = {
            "title": "Test Product",
            "blueprint_id": 384,
            "variants": [],
            "print_areas": []
        }
        
        result = client.create_product(product_data)
        
        assert result.success == True
        assert result.data["id"] == "product_123"
        
    def test_configuration_validation(self):
        """Test configuration management"""
        config_manager = ConfigManager("test_config.json")
        
        # Test with invalid configuration
        issues = config_manager.validate_config()
        assert len(issues) > 0  # Should have validation issues
        
        # Test configuration export
        template_file = config_manager.export_config_template("test_template.json")
        assert os.path.exists(template_file)
        
        # Cleanup
        if os.path.exists("test_template.json"):
            os.remove("test_template.json")
            
    def test_image_processing_pipeline(self):
        """Test image processing functionality"""
        processor = ImageProcessor()
        
        # Test with non-existent file (should handle gracefully)
        is_valid, issues = processor.validate_image("nonexistent.jpg")
        assert not is_valid
        assert len(issues) > 0
        
        # Test prompt extraction fallback
        prompt = processor.extract_prompt_from_image("nonexistent.jpg")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

# Run integration tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 4. Automated Test Execution with MCP

```bash
#!/bin/bash
# run_automated_tests.sh

echo "🧪 Starting Enhanced Printify Automation Tool Test Suite"
echo "=================================================="

# Start application in background
echo "🚀 Starting application..."
python app.py &
APP_PID=$!
sleep 10  # Wait for application to start

# Run test suites
echo "📋 Running Playwright UI tests..."
python test_automated_workflow.py

echo "⚡ Running performance tests..."
python test_performance.py

echo "🔌 Running API integration tests..."
python test_api_integration.py

echo "🧹 Running code quality checks..."
flake8 src/ app.py --max-line-length=100
black --check src/ app.py
mypy src/ --ignore-missing-imports

# Cleanup
echo "🛑 Stopping application..."
kill $APP_PID

echo "✅ Test suite completed!"
```

## 📊 Test Results Documentation

### Expected Test Results Template

```markdown
# Test Execution Report
**Date**: [Date]
**Version**: Enhanced Printify Automation Tool v2.0
**Environment**: [Local/Docker/Production]

## Test Summary
- **Total Tests**: [Number]
- **Passed**: [Number] ✅
- **Failed**: [Number] ❌
- **Skipped**: [Number] ⏭️

## Detailed Results

### Manual Testing
| Test Suite | Test Case | Status | Notes |
|------------|-----------|--------|-------|
| Basic Functionality | Application Startup | ✅ PASS | - |
| Basic Functionality | Configuration Status | ✅ PASS | - |
| Basic Functionality | Image Analysis | ✅ PASS | - |
| Product Management | Add Product | ✅ PASS | - |
| Enhanced Upload | Single Image | ✅ PASS | - |
| Enhanced Upload | Batch Images | ✅ PASS | - |
| Error Handling | Network Errors | ✅ PASS | - |

### Automated Testing
| Test Suite | Status | Duration | Notes |
|------------|--------|----------|-------|
| Playwright UI Tests | ✅ PASS | 45s | All workflows functional |
| Performance Tests | ✅ PASS | 30s | Response times acceptable |
| API Integration | ✅ PASS | 15s | Mocked API calls working |

## Issues Found
[List any issues discovered during testing]

## Performance Metrics
- **Application Startup**: [X.X]s
- **Average Response Time**: [X.X]s
- **Memory Usage**: [X]MB peak
- **Concurrent User Capacity**: [X] users

## Recommendations
[Any recommendations for improvements or next steps]
```

## 🎯 Next Steps for MCP Tool Integration

### When MCP Tools Are Available:

1. **Automated Test Execution**
   ```bash
   # MCP can run this automatically
   ./run_automated_tests.sh
   ```

2. **Continuous Integration Setup**
   ```yaml
   # .github/workflows/test.yml
   name: Test Suite
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Setup Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.9
         - name: Install dependencies
           run: pip install -r requirements.txt
         - name: Run tests
           run: ./run_automated_tests.sh
   ```

3. **Test Data Generation**
   ```python
   # MCP can generate test images automatically
   python create_test_images.py
   ```

4. **Performance Monitoring**
   ```python
   # MCP can run regular performance checks
   python test_performance.py --continuous
   ```

This comprehensive testing document provides clear instructions for both manual and automated testing, ensuring the Enhanced Printify Automation Tool can be thoroughly validated by either human testers or automated systems using MCP tools.