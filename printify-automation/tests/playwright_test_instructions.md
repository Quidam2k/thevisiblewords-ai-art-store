
🎭 Playwright Browser Testing Instructions

1. Start the Gradio app:
   python app.py

2. Use the MCP Playwright server to test these scenarios:

📦 Product Management Tab Tests:
• Navigate to http://localhost:7860
• Click on "Product Management" tab
• Test adding a product with a Printify catalog link
• Verify product appears in the list
• Test deleting a product
• Test clearing all products

🖼️ Enhanced Upload Tab Tests:
• Click on "Enhanced Upload" tab  
• Upload test images (PNG/JPG with EXIF data)
• Click "Smart Upload & Create Products"
• Verify processing status updates
• Check detailed results

⚙️ Configuration Tab Tests:
• Click on "Configuration" tab
• Check configuration status display
• Test "Refresh Status" button
• Check error summary section
• Test "Refresh Errors" button

📊 Analytics Tab Tests:
• Click on "Analytics" tab
• Test "Refresh Analytics" button
• Verify activity and performance metrics display

🛠️ Tools Tab Tests:
• Click on "Tools" tab
• Upload an image for analysis
• Click "Analyze Image" button
• Verify analysis results
• Test configuration tools

Example Playwright MCP commands:
```
# Navigate to app
mcp__playwright__browser_navigate("http://localhost:7860")

# Take screenshot of main interface
mcp__playwright__browser_take_screenshot("gradio-main-interface.png")

# Click on Product Management tab
mcp__playwright__browser_click("Product Management tab", "tab_ref")

# Type in product link field
mcp__playwright__browser_type("product link input", "input_ref", "https://printify.com/catalog/product/...")

# Click add product button
mcp__playwright__browser_click("Add Product button", "button_ref")

# Take screenshot of results
mcp__playwright__browser_take_screenshot("product-added-result.png")
```

🔍 Key Elements to Test:
• Tab navigation functionality
• Form input and submission
• Button click responses
• Dynamic content updates
• Error message displays
• Status indicators
• File upload functionality
• Progress bars and loading states
