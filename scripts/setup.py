#!/usr/bin/env python3
"""
The Visible Words - Project Setup Script
Automated setup for the AI Art Automation Platform
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import argparse

class ProjectSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.automation_dir = self.project_root / "printify-automation"
        self.config_dir = self.automation_dir / "config"
        
    def print_banner(self):
        """Print project banner"""
        print("""
🎨 =====================================================
   The Visible Words - AI Art Automation Platform
   Project Setup & Configuration Tool
=====================================================
        """)
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required. Current version:", sys.version)
            return False
        print("✅ Python version:", sys.version.split()[0])
        
        # Check if pip is available
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("✅ pip is available")
        except subprocess.CalledProcessError:
            print("❌ pip is not available")
            return False
        
        # Check if virtual environment tools are available
        try:
            subprocess.run([sys.executable, "-m", "venv", "--help"], 
                         check=True, capture_output=True)
            print("✅ venv is available")
        except subprocess.CalledProcessError:
            print("⚠️  venv not available, will use global Python environment")
        
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        venv_path = self.automation_dir / "venv"
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("🔧 Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self, dev_mode=False):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        # Determine pip executable
        venv_path = self.automation_dir / "venv"
        if venv_path.exists():
            if os.name == 'nt':  # Windows
                pip_executable = venv_path / "Scripts" / "pip"
            else:  # Unix/Linux/macOS
                pip_executable = venv_path / "bin" / "pip"
        else:
            pip_executable = "pip"
        
        # Install main requirements
        requirements_file = self.project_root / "requirements.txt"
        
        try:
            subprocess.run([
                str(pip_executable), "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Main dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
        
        # Install automation-specific requirements
        automation_requirements = self.automation_dir / "requirements.txt"
        if automation_requirements.exists():
            try:
                subprocess.run([
                    str(pip_executable), "install", "-r", str(automation_requirements)
                ], check=True)
                print("✅ Automation dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Some automation dependencies failed: {e}")
        
        return True
    
    def setup_configuration(self):
        """Set up configuration files"""
        print("⚙️  Setting up configuration...")
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Copy configuration template
        template_file = self.config_dir / "config.template.json"
        config_file = self.config_dir / "config.json"
        
        if not config_file.exists() and template_file.exists():
            shutil.copy(template_file, config_file)
            print("✅ Configuration template copied to config.json")
            print("🔧 Please edit config.json with your Printify API credentials")
        elif config_file.exists():
            print("✅ Configuration file already exists")
        else:
            # Create a basic configuration template
            basic_config = {
                "api": {
                    "access_token": "YOUR_PRINTIFY_ACCESS_TOKEN_HERE",
                    "shop_id": "YOUR_SHOP_ID_HERE",
                    "base_url": "https://api.printify.com/v1",
                    "v2_base_url": "https://api.printify.com/v2",
                    "user_agent": "Printify-Automation-Tool",
                    "rate_limit_rpm": 600,
                    "retry_attempts": 3
                },
                "image_processing": {
                    "max_width": 4000,
                    "max_height": 4000,
                    "quality": 90,
                    "format": "JPEG",
                    "optimize": True
                },
                "tag_settings": {
                    "max_tags": 15,
                    "min_tag_length": 3,
                    "custom_tag_templates": ["ai-art", "digital-art"]
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(basic_config, f, indent=4)
            print("✅ Basic configuration created")
            print("🔧 Please edit config.json with your Printify API credentials")
        
        return True
    
    def setup_environment_file(self):
        """Create .env file for environment variables"""
        env_file = self.automation_dir / ".env"
        
        if env_file.exists():
            print("✅ Environment file already exists")
            return True
        
        env_content = """# The Visible Words - Environment Configuration
# Copy this file to .env and fill in your actual values

# Database Configuration
DATABASE_URL=sqlite:///./printify_automation.db

# Redis Configuration (for caching and sessions)
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Printify API (can also be configured in config.json)
PRINTIFY_ACCESS_TOKEN=your-printify-access-token
PRINTIFY_SHOP_ID=your-shop-id

# Development/Production Mode
ENVIRONMENT=development
DEBUG=true

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn-for-error-tracking

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Environment file template created")
        print("🔧 Please edit .env with your actual values")
        return True
    
    def install_node_dependencies(self):
        """Install Node.js dependencies for browser testing"""
        package_json = self.automation_dir / "package.json"
        
        if not package_json.exists():
            print("⚠️  No package.json found, skipping Node.js setup")
            return True
        
        print("📦 Installing Node.js dependencies...")
        
        try:
            subprocess.run(["npm", "install"], 
                         cwd=self.automation_dir, check=True)
            print("✅ Node.js dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to install Node.js dependencies: {e}")
            print("   Browser testing may not work properly")
        except FileNotFoundError:
            print("⚠️  npm not found. Install Node.js for browser testing features")
        
        return True
    
    def run_initial_tests(self):
        """Run basic tests to verify setup"""
        print("🧪 Running initial tests...")
        
        # Test import of core modules
        try:
            sys.path.insert(0, str(self.automation_dir))
            from src.config_manager import ConfigManager
            config_manager = ConfigManager(str(self.config_dir / "config.json"))
            print("✅ Core modules import successfully")
        except ImportError as e:
            print(f"⚠️  Some modules failed to import: {e}")
            return False
        
        # Test configuration loading
        try:
            if config_manager.is_configured():
                print("✅ Configuration is valid")
            else:
                issues = config_manager.validate_config()
                print("⚠️  Configuration needs attention:")
                for issue in issues:
                    print(f"    - {issue}")
        except Exception as e:
            print(f"⚠️  Configuration validation error: {e}")
        
        return True
    
    def display_next_steps(self):
        """Display next steps for the user"""
        print("""
🎉 Setup Complete! Next Steps:
===============================

1. 📝 Configure API Credentials:
   Edit: printify-automation/config/config.json
   Add your Printify access token and shop ID
   Get credentials from: https://printify.com/app/account/api

2. 🔧 Set Environment Variables:
   Edit: printify-automation/.env
   Configure database, security, and other settings

3. 🚀 Start the Application:
   cd printify-automation
   python app.py
   
   Or activate virtual environment first:
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate     # Windows
   python app.py

4. 🌐 Access Web Interface:
   Open: http://localhost:7860

5. 🧪 Run Tests:
   cd printify-automation
   python tests/run_tests.py

6. 📚 Read Documentation:
   See: printify-automation/docs/

🔗 Quick Links:
- User Guide: printify-automation/docs/USER_WORKFLOW_GUIDE.md
- API Reference: printify-automation/docs/api-reference.md
- Testing Guide: printify-automation/docs/TESTING.md

Happy automating! 🎨✨
        """)
    
    def run_setup(self, dev_mode=False, skip_venv=False):
        """Run complete setup process"""
        self.print_banner()
        
        if not self.check_prerequisites():
            return False
        
        if not skip_venv:
            if not self.create_virtual_environment():
                return False
        
        if not self.install_dependencies(dev_mode):
            return False
        
        if not self.setup_configuration():
            return False
        
        if not self.setup_environment_file():
            return False
        
        self.install_node_dependencies()
        
        if not self.run_initial_tests():
            print("⚠️  Some tests failed, but setup can continue")
        
        self.display_next_steps()
        return True

def main():
    parser = argparse.ArgumentParser(description="Setup The Visible Words AI Art Automation Platform")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")
    
    args = parser.parse_args()
    
    setup = ProjectSetup()
    success = setup.run_setup(dev_mode=args.dev, skip_venv=args.skip_venv)
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup encountered errors. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()