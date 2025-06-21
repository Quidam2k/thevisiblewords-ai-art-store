import gradio as gr
import pandas as pd
import json
import os
import sys
import threading
import time
import requests
from datetime import datetime
from PIL import Image, ExifTags
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our enhanced modules
from tag_generator import SmartTagGenerator
from config_manager import ConfigManager, ProductSettings
from image_processor import ImageProcessor
from api_client import PrintifyAPIClient
from error_handler import ErrorHandler, ErrorContext
from print_area_manager import PrintAreaManager, PrintPosition

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPrintifyApp:
    def __init__(self):
        # Initialize enhanced components
        self.config_manager = ConfigManager()
        self.error_handler = ErrorHandler()
        self.tag_generator = SmartTagGenerator()
        self.print_area_manager = PrintAreaManager()
        
        # Initialize with configuration
        config = self.config_manager.config
        api_settings = self.config_manager.get_api_settings()
        image_settings = self.config_manager.get_image_processing_settings()
        
        self.image_processor = ImageProcessor(config=image_settings.__dict__)
        
        # Initialize API client if credentials are available
        self.api_client = None
        if api_settings.access_token and api_settings.shop_id:
            try:
                self.api_client = PrintifyAPIClient(
                    api_settings.access_token,
                    api_settings.shop_id,
                    config=api_settings.__dict__
                )
            except Exception as e:
                logger.error(f"Failed to initialize API client: {e}")
        
        # Legacy compatibility
        self.access_token = api_settings.access_token
        self.shop_id = api_settings.shop_id
        self.base_url = api_settings.base_url
        self.data_file = 'products_providers.json'
        self.upload_log_file = 'printify_upload.log'
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Config file not found. Please create config.json with your Printify credentials.")
            return {}
    
    def load_data(self):
        """Load product data from JSON file"""
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_data(self, data):
        """Save product data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def extract_prompt_from_image(self, image_path):
        """Extract prompt from image EXIF data"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if not exif_data:
                    return "No prompt found"
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    if tag_name == 'ImageDescription':
                        return value
        except Exception as e:
            logger.error(f"Error extracting prompt from {image_path}: {str(e)}")
        return "No prompt found"
    
    def fetch_providers(self, blueprint_id):
        """Fetch available print providers for a blueprint"""
        if not self.access_token:
            return []
        
        providers_url = f"{self.base_url}/catalog/blueprints/{blueprint_id}/print_providers.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(providers_url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch providers: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching providers: {str(e)}")
            return []
    
    def add_product_link(self, product_link):
        """Add a product from Printify catalog link"""
        if not product_link:
            return "Please enter a product link", self.get_product_list()
        
        try:
            # Extract blueprint ID from URL
            blueprint_id = int(product_link.split("/")[-3])
            providers = self.fetch_providers(blueprint_id)
            
            if not providers:
                return "No providers found for this product", self.get_product_list()
            
            # If only one provider, add it directly
            if len(providers) == 1:
                provider = providers[0]
                record = {
                    "blueprint_id": blueprint_id,
                    "provider": {
                        "id": provider['id'],
                        "title": provider['title']
                    }
                }
                data = self.load_data()
                data.append(record)
                self.save_data(data)
                return f"Product added with provider: {provider['title']}", self.get_product_list()
            else:
                # Multiple providers - return selection options
                provider_options = [f"{p['title']} (ID: {p['id']})" for p in providers]
                return f"Multiple providers found. Blueprint ID: {blueprint_id}", self.get_product_list()
                
        except (ValueError, IndexError) as e:
            return f"Invalid product link format: {str(e)}", self.get_product_list()
    
    def get_product_list(self):
        """Get formatted list of products for display"""
        data = self.load_data()
        if not data:
            return "No products configured"
        
        products = []
        for i, record in enumerate(data):
            blueprint_id = record.get('blueprint_id', 'Unknown')
            provider_title = record.get('provider', {}).get('title', 'Unknown')
            products.append(f"{i+1}. Blueprint ID: {blueprint_id} - Provider: {provider_title}")
        
        return "\n".join(products)
    
    def delete_product(self, product_index):
        """Delete a product by index"""
        try:
            index = int(product_index) - 1
            data = self.load_data()
            if 0 <= index < len(data):
                removed = data.pop(index)
                self.save_data(data)
                return f"Deleted product: {removed.get('blueprint_id', 'Unknown')}", self.get_product_list()
            else:
                return "Invalid product index", self.get_product_list()
        except ValueError:
            return "Please enter a valid number", self.get_product_list()
    
    def clear_all_products(self):
        """Clear all products"""
        self.save_data([])
        return "All products cleared", self.get_product_list()
    
    def upload_products(self, image_files, progress=gr.Progress()):
        """Enhanced upload with smart processing, optimization, and error handling"""
        if not image_files:
            return "No images selected", ""
        
        if not self.api_client:
            return "Please configure Printify credentials in config.json", ""
        
        # Get product settings from configuration
        product_settings = self.config_manager.get_product_settings()
        if not product_settings:
            return "No products configured. Please add products first.", ""
        
        results = []
        total_images = len(image_files)
        total_operations = total_images * len(product_settings)
        operation_count = 0
        
        progress(0, desc="Starting enhanced upload...")
        
        for img_idx, image_file in enumerate(image_files):
            file_path = image_file.name
            filename = os.path.basename(file_path)
            
            with ErrorContext(self.error_handler, {"operation": "process_image", "file": filename}):
                try:
                    # Phase 1: Image Processing and Validation
                    progress((operation_count / total_operations) * 100, 
                           desc=f"Processing {filename} ({img_idx + 1}/{total_images})")
                    
                    # Validate image
                    is_valid, issues = self.image_processor.validate_image(file_path)
                    if not is_valid:
                        results.append(f"❌ {filename}: {'; '.join(issues)}")
                        operation_count += len(product_settings)
                        continue
                    
                    # Optimize image
                    optimized_path, image_info = self.image_processor.optimize_image(file_path)
                    
                    # Extract enhanced prompt
                    prompt = self.image_processor.extract_prompt_from_image(file_path)
                    
                    # Generate smart tags and content
                    tags = self.tag_generator.extract_tags_from_prompt(prompt)
                    title = self.tag_generator.generate_product_title(prompt)
                    description = self.tag_generator.generate_description(prompt, title, tags)
                    
                    # Phase 2: Upload to Printify
                    progress((operation_count / total_operations) * 100, 
                           desc=f"Uploading {filename}...")
                    
                    # Convert optimized image to base64
                    img_b64 = self.image_processor.convert_to_base64(optimized_path)
                    
                    # Upload image
                    upload_response = self.api_client.upload_image(filename, img_b64)
                    if not upload_response.success:
                        results.append(f"❌ Failed to upload {filename}: {upload_response.message}")
                        operation_count += len(product_settings)
                        continue
                    
                    image_id = upload_response.data["id"]
                    preview_url = upload_response.data["preview_url"]
                    
                    # Phase 3: Create Products
                    for product_setting in product_settings:
                        operation_count += 1
                        progress((operation_count / total_operations) * 100, 
                               desc=f"Creating {product_setting.name} for {filename}...")
                        
                        try:
                            # Get variants
                            variants_response = self.api_client.get_blueprint_variants(
                                product_setting.blueprint_id,
                                self.get_default_provider_id(product_setting)
                            )
                            
                            if not variants_response.success:
                                results.append(f"❌ Failed to get variants for {product_setting.name}")
                                continue
                            
                            variants = variants_response.data.get('variants', [])
                            if not variants:
                                results.append(f"❌ No variants found for {product_setting.name}")
                                continue
                            
                            # Calculate pricing
                            base_price = self.config_manager.calculate_price(
                                1499, product_setting.pricing_tier  # Base $14.99
                            )
                            
                            # Create enhanced print areas
                            print_areas = self.create_enhanced_print_areas(
                                product_setting, variants, image_id, 
                                image_info.width, image_info.height
                            )
                            
                            # Create product with enhanced data
                            product_data = {
                                "title": title,
                                "description": description + f"\n\nFull artwork:\n<img src='{preview_url}' alt='Full Artwork'>",
                                "tags": tags,
                                "blueprint_id": product_setting.blueprint_id,
                                "print_provider_id": self.get_default_provider_id(product_setting),
                                "variants": [
                                    {
                                        "id": variant["id"],
                                        "price": base_price,
                                        "is_enabled": True
                                    } for variant in variants[:5]  # Limit to first 5 variants
                                ],
                                "print_areas": print_areas
                            }
                            
                            # Create the product
                            create_response = self.api_client.create_product(product_data)
                            if create_response.success:
                                results.append(f"✅ Created {product_setting.name} for {filename}")
                                logger.info(f"Product created: {product_setting.name} for {filename}")
                            else:
                                results.append(f"❌ Failed to create {product_setting.name} for {filename}: {create_response.message}")
                        
                        except Exception as e:
                            error_info = self.error_handler.handle_error(e, {
                                "operation": "create_product",
                                "product": product_setting.name,
                                "file": filename
                            })
                            results.append(f"❌ Error creating {product_setting.name}: {error_info.message}")
                    
                    # Clean up optimized image if different from original
                    if optimized_path != file_path:
                        try:
                            os.remove(optimized_path)
                        except:
                            pass
                
                except Exception as e:
                    error_info = self.error_handler.handle_error(e, {
                        "operation": "process_image",
                        "file": filename
                    })
                    results.append(f"❌ Error processing {filename}: {error_info.message}")
                    operation_count += len(product_settings)
        
        progress(100, desc="Upload complete!")
        
        # Generate summary
        success_count = len([r for r in results if r.startswith("✅")])
        error_count = len([r for r in results if r.startswith("❌")])
        
        summary = f"Upload completed! ✅ {success_count} successful, ❌ {error_count} errors"
        detailed_results = "\n".join(results)
        
        return summary, detailed_results
    
    def create_enhanced_print_areas(self, product_setting: ProductSettings, variants: List[Dict], 
                                  image_id: str, image_width: int, image_height: int) -> List[Dict]:
        """Create enhanced print areas with multi-position support"""
        # Determine product type from blueprint ID
        product_type = self.get_product_type_from_blueprint(product_setting.blueprint_id)
        
        # Get available positions for this product
        available_positions = self.print_area_manager.get_available_positions(product_type)
        
        # Use configured positions or default
        enabled_positions = []
        for pos_str in product_setting.print_positions:
            try:
                position = PrintPosition(pos_str)
                if position in available_positions:
                    enabled_positions.append(position)
            except ValueError:
                continue
        
        if not enabled_positions:
            enabled_positions = [PrintPosition.FRONT]  # Default fallback
        
        # Create print areas
        variant_ids = [v["id"] for v in variants[:5]]  # Limit to first 5 variants
        
        print_areas = []
        for position in enabled_positions:
            config = self.print_area_manager.get_print_area_config(
                product_type, position, variant_ids, image_width, image_height
            )
            
            print_area = {
                "variant_ids": config.variant_ids,
                "placeholders": [{
                    "position": config.position.value,
                    "images": [{
                        "id": image_id,
                        "x": config.placement.x,
                        "y": config.placement.y,
                        "scale": config.placement.scale,
                        "angle": config.placement.angle
                    }]
                }]
            }
            print_areas.append(print_area)
        
        return print_areas
    
    def get_product_type_from_blueprint(self, blueprint_id: int) -> str:
        """Map blueprint ID to product type"""
        blueprint_map = {
            384: "tshirt",
            5: "poster",
            9: "mug",
            6: "canvas",
            12: "phone_case"
        }
        return blueprint_map.get(blueprint_id, "tshirt")
    
    def get_default_provider_id(self, product_setting: ProductSettings) -> int:
        """Get default provider ID for a product setting"""
        # Try to get from loaded data first
        data = self.load_data()
        for record in data:
            if record.get('blueprint_id') == product_setting.blueprint_id:
                provider_id = record.get('provider', {}).get('id')
                if provider_id:
                    return provider_id
        
        # If no stored provider, fetch from API and use first available
        if self.api_client:
            providers_response = self.api_client.get_blueprint_providers(product_setting.blueprint_id)
            if providers_response.success and providers_response.data:
                providers = providers_response.data
                if providers:
                    return providers[0]['id']
        
        # Fallback to common provider IDs based on blueprint
        provider_defaults = {
            384: 1,   # T-shirt - Generic provider
            5: 3,     # Poster - Generic poster provider
            9: 5,     # Mug - Generic mug provider
            6: 3,     # Canvas - Generic canvas provider
            12: 15    # Phone case - Generic phone case provider
        }
        
        return provider_defaults.get(product_setting.blueprint_id, 1)
    
    def get_configuration_status(self) -> str:
        """Get current configuration status"""
        if not self.config_manager.is_configured():
            issues = self.config_manager.validate_config()
            return f"❌ Configuration issues:\n" + "\n".join(f"• {issue}" for issue in issues)
        
        api_settings = self.config_manager.get_api_settings()
        product_count = len(self.config_manager.get_product_settings())
        
        # Test API connection if possible
        connection_status = "Unknown"
        if self.api_client:
            try:
                is_valid, message = self.api_client.validate_credentials()
                connection_status = "✅ Connected" if is_valid else f"❌ {message}"
            except Exception as e:
                connection_status = f"❌ Connection error: {str(e)}"
        
        return f"""✅ Configuration Status:
• API Connection: {connection_status}
• Shop ID: {api_settings.shop_id}
• Products Configured: {product_count}
• Image Processing: Enabled with optimization
• Smart Tags: Enabled
• Error Handling: Enhanced with retry logic"""

    def get_error_summary(self) -> str:
        """Get recent error summary"""
        summary = self.error_handler.get_error_summary(24)  # Last 24 hours
        
        if summary["total_errors"] == 0:
            return "✅ No errors in the last 24 hours"
        
        error_text = f"⚠️ {summary['total_errors']} errors in last 24 hours:\n"
        
        for category, count in summary["by_category"].items():
            error_text += f"• {category}: {count}\n"
        
        if summary["most_common"]:
            error_text += "\nMost common issues:\n"
            for error, count in summary["most_common"][:3]:
                error_text += f"• {error[:50]}... ({count}x)\n"
        
        return error_text

def create_interface():
    app = EnhancedPrintifyApp()
    
    with gr.Blocks(title="Enhanced Printify Automation Tool", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🚀 Enhanced Printify Automation Tool")
        gr.Markdown("**AI-powered image processing with smart tags, optimization, and multi-position printing**")
        
        with gr.Tab("📦 Product Management"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add Products")
                    product_link_input = gr.Textbox(
                        label="Printify Product Link",
                        placeholder="Paste Printify catalog link here...",
                        lines=1
                    )
                    add_product_btn = gr.Button("Add Product", variant="primary")
                    add_result = gr.Textbox(label="Result", lines=2)
                
                with gr.Column():
                    gr.Markdown("### Manage Products")
                    product_index_input = gr.Textbox(
                        label="Product Index to Delete",
                        placeholder="Enter number (e.g., 1, 2, 3...)",
                        lines=1
                    )
                    delete_product_btn = gr.Button("Delete Product", variant="secondary")
                    clear_all_btn = gr.Button("Clear All Products", variant="stop")
            
            gr.Markdown("### Current Products")
            product_list = gr.Textbox(
                label="Configured Products",
                value=app.get_product_list(),
                lines=10,
                interactive=False
            )
        
        with gr.Tab("🖼️ Enhanced Upload"):
            gr.Markdown("### 🎯 Smart AI-Powered Processing")
            gr.Markdown("""
            **Features:**
            • **Smart Tag Generation** - Automatically extracts relevant tags from AI prompts
            • **Image Optimization** - Resizes and optimizes images for best quality
            • **Multi-Position Printing** - Supports front, back, sleeves, and more
            • **Configurable Pricing** - Uses pricing tiers from configuration
            • **Error Recovery** - Intelligent retry logic and error handling
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Select Images")
                    image_input = gr.File(
                        label="Upload AI-Generated Images",
                        file_count="multiple",
                        file_types=[".png", ".jpg", ".jpeg"],
                        height=200
                    )
                    gr.Markdown("*Supports PNG, JPG, JPEG with EXIF metadata*")
                    upload_btn = gr.Button("🚀 Smart Upload & Create Products", variant="primary", size="lg")
                
                with gr.Column():
                    gr.Markdown("### Processing Status")
                    upload_status = gr.Textbox(label="Status", lines=2)
                    upload_results = gr.Textbox(
                        label="Detailed Results",
                        lines=15,
                        interactive=False,
                        show_copy_button=True
                    )
        
        with gr.Tab("⚙️ Configuration"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### System Status")
                    config_status = gr.Textbox(
                        label="Configuration Status",
                        value=app.get_configuration_status(),
                        lines=8,
                        interactive=False
                    )
                    refresh_status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                
                with gr.Column():
                    gr.Markdown("### Error Summary")
                    error_summary = gr.Textbox(
                        label="Recent Errors (24h)",
                        value=app.get_error_summary(),
                        lines=8,
                        interactive=False
                    )
                    refresh_errors_btn = gr.Button("🔄 Refresh Errors", variant="secondary")
            
            gr.Markdown("### Setup Instructions")
            gr.Markdown("""
            **Quick Setup:**
            1. **Get API Credentials** from [Printify Dashboard](https://printify.com/app/account/api)
            2. **Create config.json** in the project directory:
            ```json
            {
                "api": {
                    "access_token": "your_printify_access_token",
                    "shop_id": "your_shop_id"
                }
            }
            ```
            3. **Configure Products** using Printify catalog links
            4. **Upload Images** with AI prompts in EXIF metadata
            
            **Advanced Features:**
            • **Pricing Tiers** - Configure different pricing strategies
            • **Image Processing** - Customize optimization settings  
            • **Tag Generation** - Control automatic tag creation
            • **Print Positions** - Enable multiple print areas per product
            
            See `config-template.json` for full configuration options.
            """)
        
        with gr.Tab("📊 Analytics"):
            gr.Markdown("### Upload Analytics")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Recent Activity")
                    activity_summary = gr.Textbox(
                        label="Activity Summary",
                        lines=6,
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("#### Performance Metrics")
                    performance_metrics = gr.Textbox(
                        label="Performance Metrics",
                        lines=6,
                        interactive=False
                    )
            
            refresh_analytics_btn = gr.Button("🔄 Refresh Analytics", variant="secondary")
        
        with gr.Tab("🛠️ Tools"):
            gr.Markdown("### Utility Tools")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Image Preview & Analysis")
                    preview_image = gr.File(
                        label="Select Image for Analysis",
                        file_types=[".png", ".jpg", ".jpeg"]
                    )
                    analyze_btn = gr.Button("🔍 Analyze Image", variant="primary")
                    
                with gr.Column():
                    analysis_result = gr.Textbox(
                        label="Analysis Results",
                        lines=10,
                        interactive=False
                    )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Configuration Tools")
                    export_config_btn = gr.Button("📥 Export Config Template", variant="secondary")
                    validate_config_btn = gr.Button("✅ Validate Configuration", variant="secondary")
                
                with gr.Column():
                    tool_results = gr.Textbox(
                        label="Tool Results",
                        lines=6,
                        interactive=False
                    )
        
        # Helper functions for new features
        def analyze_image(image_file):
            if not image_file:
                return "No image selected"
            
            try:
                # Get image info
                with Image.open(image_file.name) as img:
                    width, height = img.size
                    format_name = img.format
                
                # Extract prompt and metadata
                prompt = app.image_processor.extract_prompt_from_image(image_file.name)
                exif_data = app.image_processor.extract_comprehensive_exif(image_file.name)
                
                # Generate tags
                tags = app.tag_generator.extract_tags_from_prompt(prompt)
                title = app.tag_generator.generate_product_title(prompt)
                
                # Get position recommendations
                recommendations = app.print_area_manager.get_position_recommendations(width, height, "tshirt")
                
                analysis = f"""📷 **Image Analysis**
**Dimensions:** {width} x {height} pixels ({format_name})
**Extracted Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}

🏷️ **Generated Tags:** {', '.join(tags[:10])}
📝 **Generated Title:** {title}

🎯 **Print Position Recommendations:**"""
                
                for position, rec in list(recommendations.items())[:3]:
                    analysis += f"\n• **{position.value}**: {rec['compatibility_score']:.2f} compatibility - {rec['recommended_strategy']}"
                
                if exif_data:
                    analysis += f"\n\n📋 **Metadata Found:** {len(exif_data)} EXIF fields"
                
                return analysis
                
            except Exception as e:
                error_info = app.error_handler.handle_error(e, {"operation": "analyze_image"})
                return f"❌ Analysis failed: {error_info.message}"
        
        def export_config_template():
            try:
                template_file = app.config_manager.export_config_template()
                return f"✅ Configuration template exported to: {template_file}"
            except Exception as e:
                return f"❌ Export failed: {str(e)}"
        
        def validate_configuration():
            try:
                if app.config_manager.is_configured():
                    return "✅ Configuration is valid and complete"
                else:
                    issues = app.config_manager.validate_config()
                    return "❌ Configuration issues:\n" + "\n".join(f"• {issue}" for issue in issues)
            except Exception as e:
                return f"❌ Validation failed: {str(e)}"
        
        def refresh_analytics():
            """Refresh analytics with real data"""
            try:
                # Get error summary for activity
                error_summary = app.get_error_summary()
                
                # Calculate activity summary
                total_errors = error_summary.get("total_errors", 0)
                by_category = error_summary.get("by_category", {})
                
                if total_errors == 0:
                    activity_text = "✅ No errors in the last 24 hours\n📈 System running smoothly"
                else:
                    activity_text = f"⚠️ {total_errors} errors in last 24 hours\n"
                    for category, count in by_category.items():
                        activity_text += f"• {category}: {count}\n"
                
                # Performance metrics
                performance_text = "⚡ Performance Metrics:\n"
                
                # Check if API client is available and working
                if app.api_client:
                    try:
                        is_valid, message = app.api_client.validate_credentials()
                        if is_valid:
                            performance_text += "• API Connection: ✅ Active\n"
                            performance_text += "• Rate Limiting: ✅ Enabled\n"
                            performance_text += "• Retry Logic: ✅ Active\n"
                        else:
                            performance_text += f"• API Connection: ❌ {message}\n"
                    except Exception as e:
                        performance_text += f"• API Connection: ❌ Error: {str(e)[:50]}\n"
                else:
                    performance_text += "• API Connection: ⚠️ Not configured\n"
                
                # Check configuration status
                config_issues = app.config_manager.validate_config()
                if not config_issues:
                    performance_text += "• Configuration: ✅ Valid\n"
                else:
                    performance_text += f"• Configuration: ⚠️ {len(config_issues)} issues\n"
                
                # Check product settings
                product_settings = app.config_manager.get_product_settings()
                performance_text += f"• Products Configured: {len(product_settings)}\n"
                
                # Memory and processing info
                try:
                    import psutil
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    performance_text += f"• Memory Usage: {memory_mb:.1f} MB\n"
                except ImportError:
                    performance_text += "• Memory Usage: N/A (psutil not installed)\n"
                
                performance_text += f"• Last Updated: {datetime.now().strftime('%H:%M:%S')}"
                
                return activity_text, performance_text
                
            except Exception as e:
                error_text = f"❌ Failed to refresh analytics: {str(e)}"
                return error_text, "⚠️ Performance data unavailable"
        
        # Event handlers
        add_product_btn.click(
            fn=app.add_product_link,
            inputs=[product_link_input],
            outputs=[add_result, product_list]
        )
        
        delete_product_btn.click(
            fn=app.delete_product,
            inputs=[product_index_input],
            outputs=[add_result, product_list]
        )
        
        clear_all_btn.click(
            fn=app.clear_all_products,
            outputs=[add_result, product_list]
        )
        
        upload_btn.click(
            fn=app.upload_products,
            inputs=[image_input],
            outputs=[upload_status, upload_results]
        )
        
        # New enhanced event handlers
        refresh_status_btn.click(
            fn=app.get_configuration_status,
            outputs=[config_status]
        )
        
        refresh_errors_btn.click(
            fn=app.get_error_summary,
            outputs=[error_summary]
        )
        
        analyze_btn.click(
            fn=analyze_image,
            inputs=[preview_image],
            outputs=[analysis_result]
        )
        
        export_config_btn.click(
            fn=export_config_template,
            outputs=[tool_results]
        )
        
        validate_config_btn.click(
            fn=validate_configuration,
            outputs=[tool_results]
        )
        
        refresh_analytics_btn.click(
            fn=refresh_analytics,
            outputs=[activity_summary, performance_metrics]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True
    )