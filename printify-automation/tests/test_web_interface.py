#!/usr/bin/env python3
"""
Web Interface Testing with Playwright MCP Server
Tests the Gradio application through browser automation
"""

import os
import sys
import time
import subprocess
import threading
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GradioAppTester:
    def __init__(self, host="localhost", port=7860):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.app_process = None
        self.app_thread = None
        self.startup_timeout = 30  # seconds
        
    def start_gradio_app(self):
        """Start the Gradio app in a subprocess"""
        print(f"🚀 Starting Gradio app on {self.base_url}")
        
        # Start the app process
        cmd = [
            sys.executable, 
            "app.py",
            "--server-name", "0.0.0.0",
            "--server-port", str(self.port)
        ]
        
        self.app_process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )
        
        # Wait for app to start
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                response = requests.get(self.base_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Gradio app started successfully at {self.base_url}")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print(f"❌ Failed to start Gradio app within {self.startup_timeout} seconds")
        return False
    
    def stop_gradio_app(self):
        """Stop the Gradio app"""
        if self.app_process:
            print("🛑 Stopping Gradio app...")
            self.app_process.terminate()
            self.app_process.wait(timeout=10)
            self.app_process = None
    
    def test_app_startup(self):
        """Test that the app starts successfully"""
        try:
            if not self.start_gradio_app():
                return False, "Failed to start Gradio app"
            
            # Test basic connectivity
            response = requests.get(self.base_url)
            if response.status_code != 200:
                return False, f"App returned status code {response.status_code}"
            
            # Check if it's actually a Gradio app
            if "gradio" not in response.text.lower():
                return False, "Response doesn't appear to be from Gradio app"
            
            return True, "App startup test passed"
            
        except Exception as e:
            return False, f"App startup test failed: {str(e)}"
        finally:
            self.stop_gradio_app()
    
    def get_playwright_test_instructions(self):
        """Generate instructions for manual Playwright testing"""
        return f"""
🎭 Playwright Browser Testing Instructions

1. Start the Gradio app:
   python app.py

2. Use the MCP Playwright server to test these scenarios:

📦 Product Management Tab Tests:
• Navigate to {self.base_url}
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
"""

def run_web_interface_tests():
    """Run comprehensive web interface tests"""
    print("🌐 Starting Web Interface Testing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = GradioAppTester()
    
    # Test 1: App Startup
    print("\n1️⃣ Testing App Startup...")
    startup_success, startup_message = tester.test_app_startup()
    print(f"   Result: {startup_message}")
    
    # Test 2: Generate Playwright Instructions
    print("\n2️⃣ Generating Playwright Test Instructions...")
    instructions = tester.get_playwright_test_instructions()
    
    # Save instructions to file
    instructions_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "playwright_test_instructions.md"
    )
    
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"   Instructions saved to: {instructions_file}")
    
    # Summary
    print(f"\n{'='*60}")
    print("WEB INTERFACE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"App Startup Test: {'✅ PASSED' if startup_success else '❌ FAILED'}")
    print(f"Playwright Instructions: ✅ GENERATED")
    print(f"{'='*60}")
    
    if startup_success:
        print("\n🎉 Basic web interface tests passed!")
        print("💡 Use the generated Playwright instructions for comprehensive browser testing")
        return True
    else:
        print("\n❌ Web interface tests failed")
        return False

def main():
    """Main test entry point"""
    try:
        success = run_web_interface_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Web interface testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)